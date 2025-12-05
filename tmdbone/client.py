import asyncio
import aiohttp
import logging
from itertools import cycle
from typing import List, Set, Optional, Any

from .exceptions import TMDbAPIError
from .utils import TMDbImageHelper
from .resources import (
    Movie, TV, Person, Find, Discover, Collection, Company, Network,
    Search, Trending, Genre, Configuration, Keyword, Review, Certification, Credit
)

class TMDbOneClient:
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(
        self,
        api_keys: List[str],
        language: Optional[str] = 'en-US',
        region: Optional[str] = None,
        retries: int = 3,
        retry_delay: int = 5,
        default_cooldown: int = 10,
        timeout: int = 30,
        session: Optional[aiohttp.ClientSession] = None
    ):
        if not api_keys:
            raise ValueError("At least one TMDb API key is required.")
        
        self.language = language
        self.region = region
        self.active_api_keys: Set[str] = set(api_keys)
        self.api_key_rotator = cycle(list(self.active_api_keys))
        
        self.retries = retries
        self.retry_delay = retry_delay
        self.default_cooldown = default_cooldown
        self.timeout = timeout
        
        self._external_session = session is not None
        self.session = session 
        self.images = TMDbImageHelper

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _get_session(self) -> aiohttp.ClientSession:
        """
        Retrieves the existing session or creates a new one.
        Ensures the session matches the CURRENT running event loop.
        """
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            raise TMDbAPIError("TMDbOneClient must be used inside an async function (event loop running).")

        if self.session and not self.session.closed:
            is_same_loop = True
            try:
                if self.session.loop is not current_loop:
                    is_same_loop = False
            except AttributeError:
                pass
            
            if is_same_loop:
                return self.session
            
            if self._external_session:
                raise TMDbAPIError("External session is bound to a different event loop.")
            
            self.session = None

        timeout_settings = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(
            headers={'User-Agent': f'TMDbOneClient/3.0.0'},
            timeout=timeout_settings
        )
        return self.session

    def _sanitize_params(self, params: dict) -> dict:
        """
        Cleans parameters:
        1. Drops None values.
        2. Bools -> 'true'/'false'.
        3. Lists/Tuples -> comma-joined strings.
        """
        clean = {}
        for k, v in params.items():
            if v is None:
                continue
            
            if isinstance(v, bool):
                clean[k] = str(v).lower()
            elif isinstance(v, (list, tuple)):
                items = [str(x) for x in v if x is not None]
                if items:
                    clean[k] = ",".join(items)
            else:
                clean[k] = v
        return clean

    async def _api_request(self, method: str, url: str, params: Optional[dict] = None) -> Optional[dict]:
        if params is None: params = {}
        
        if self.language: params.setdefault('language', self.language)
        if self.region: params.setdefault('region', self.region)
        
        network_attempts = 0
        max_rate_limit_retries = 5
        rate_limit_attempts = 0
        
        last_exception = None

        while True:
            if not self.active_api_keys:
                raise TMDbAPIError("All API keys have been invalidated or exhausted.")
            
            if network_attempts > self.retries:
                break

            current_api_key = next(self.api_key_rotator)
            
            request_params = self._sanitize_params(params)
            request_params['api_key'] = current_api_key
            
            session = self._get_session()

            try:
                async with session.request(method, url, params=request_params) as response:
                    
                   
                    if response.status == 200:
                        try:
                            return await response.json()
                        except (aiohttp.ContentTypeError, ValueError):
                         
                            text = await response.text()
                            raise TMDbAPIError(f"API returned non-JSON response.", status_code=200, url=url, response_body=text)
                    if response.status == 404:
                        return None
                        
                    if response.status == 401:
                        logging.warning(f"Invalid API Key (...{current_api_key[-4:]}). Removing from rotation.")
                        self.active_api_keys.discard(current_api_key)
                        if self.active_api_keys:
                            self.api_key_rotator = cycle(list(self.active_api_keys))
                        continue 
                    if response.status == 429:
                        if rate_limit_attempts >= max_rate_limit_retries:
                            raise TMDbAPIError("Max rate limit retries exceeded.", status_code=429, url=url)
                        
                        retry_after = response.headers.get("Retry-After")
                        sleep_time = self.default_cooldown
                        
                        if retry_after:
                            try:
                                sleep_time = float(retry_after)
                            except ValueError:
                                pass
                        
                        logging.warning(f"Rate limit hit (429). Sleeping {sleep_time}s.")
                        await asyncio.sleep(sleep_time)
                        rate_limit_attempts += 1
                        continue
                    response_body = None
                    try:
                        response_body = await response.json()
                        api_msg = response_body.get('status_message', 'Unknown Error')
                    except Exception:
                        try:
                            response_body = await response.text()
                        except:
                            response_body = "Could not read response body"
                        api_msg = response.reason

                    if 500 <= response.status < 600:
                        raise aiohttp.ClientResponseError(
                            response.request_info, response.history, 
                            status=response.status, message=api_msg
                        )
                    
                    raise TMDbAPIError(f"API Error: {api_msg}", status_code=response.status, url=url, response_body=response_body)

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                logging.warning(f"Network error attempt {network_attempts + 1}/{self.retries}: {str(e)}")
                
                network_attempts += 1
                if network_attempts <= self.retries:
                    await asyncio.sleep(self.retry_delay * network_attempts)
                    continue
                else:
                    break

      
        if last_exception:
            raise TMDbAPIError(
                f"Request failed after {network_attempts} retries.", 
                url=url
            ) from last_exception
        
        raise TMDbAPIError("Request failed unexpectedly.", url=url)

    async def close(self):
        if not self._external_session and self.session and not self.session.closed:
            await self.session.close()

    def movie(self, movie_id: int) -> Movie: return Movie(self, movie_id)
    def tv(self, tv_id: int) -> 'TV': return TV(self, tv_id)
    def person(self, person_id: int) -> 'Person': return Person(self, person_id)
    def find(self, external_id: str) -> 'Find': return Find(self, external_id)
    def discover(self) -> 'Discover': return Discover(self)
    def collection(self, collection_id: int) -> 'Collection': return Collection(self, collection_id)
    def company(self, company_id: int) -> 'Company': return Company(self, company_id)
    def network(self, network_id: int) -> 'Network': return Network(self, network_id)
    def keyword(self, keyword_id: int) -> 'Keyword': return Keyword(self, keyword_id)
    def review(self, review_id: str) -> 'Review': return Review(self, review_id)
    def credit(self, credit_id: str) -> 'Credit': return Credit(self, credit_id)
    def search(self) -> 'Search': return Search(self)
    def trending(self) -> 'Trending': return Trending(self)
    def genre(self) -> 'Genre': return Genre(self)
    def configuration(self) -> 'Configuration': return Configuration(self)
    def certification(self) -> 'Certification': return Certification(self)
    
    async def movies_now_playing(self, **kwargs): return await self._api_request("GET", f"{self.BASE_URL}/movie/now_playing", params=kwargs)
    async def movies_popular(self, **kwargs): return await self._api_request("GET", f"{self.BASE_URL}/movie/popular", params=kwargs)
    async def tv_popular(self, **kwargs): return await self._api_request("GET", f"{self.BASE_URL}/tv/popular", params=kwargs)
