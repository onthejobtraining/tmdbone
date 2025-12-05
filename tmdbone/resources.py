from typing import Optional, List, Literal, Union, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .client import TMDbOneClient

class _Resource:
    def __init__(self, client: "TMDbOneClient", path_segments: List[str]):
        self._client = client
        self._path = "/" + "/".join(map(str, path_segments))

    async def _get(self, path_suffix: str = "", **kwargs) -> Optional[dict]:
        """
        Generic GET handler.
        Merges 'append' shortcuts into 'append_to_response'.
        Sanitization occurs in Client.
        """
        if "append" in kwargs:
            val = kwargs.pop("append")
            
            if "append_to_response" in kwargs:
                existing = kwargs["append_to_response"]
                # Normalize existing to list
                if not isinstance(existing, list):
                    existing = [existing] if existing else []
                # Normalize new val to list
                if not isinstance(val, list):
                    val = [val] if val else []
                
                kwargs["append_to_response"] = existing + val
            else:
                kwargs["append_to_response"] = val

        url = f"{self._client.BASE_URL}{self._path}{path_suffix}"
        return await self._client._api_request("GET", url, params=kwargs)

class Movie(_Resource):
    def __init__(self, client, movie_id: int): super().__init__(client, ["movie", movie_id])
    async def details(self, **kwargs): return await self._get(**kwargs)
    async def alternative_titles(self, **kwargs): return await self._get("/alternative_titles", **kwargs)
    async def credits(self, **kwargs): return await self._get("/credits", **kwargs)
    async def external_ids(self, **kwargs): return await self._get("/external_ids", **kwargs)
    async def images(self, **kwargs): return await self._get("/images", **kwargs)
    async def keywords(self, **kwargs): return await self._get("/keywords", **kwargs)
    async def lists(self, **kwargs): return await self._get("/lists", **kwargs)
    async def recommendations(self, **kwargs): return await self._get("/recommendations", **kwargs)
    async def release_dates(self, **kwargs): return await self._get("/release_dates", **kwargs)
    async def reviews(self, **kwargs): return await self._get("/reviews", **kwargs)
    async def similar(self, **kwargs): return await self._get("/similar", **kwargs)
    async def translations(self, **kwargs): return await self._get("/translations", **kwargs)
    async def videos(self, **kwargs): return await self._get("/videos", **kwargs)
    async def watch_providers(self, **kwargs): return await self._get("/watch/providers", **kwargs)

class TV(_Resource):
    def __init__(self, client, tv_id: int): super().__init__(client, ["tv", tv_id]); self.tv_id = tv_id
    def season(self, season_number: int): return Season(self._client, self.tv_id, season_number)
    async def details(self, **kwargs): return await self._get(**kwargs)
    async def aggregate_credits(self, **kwargs): return await self._get("/aggregate_credits", **kwargs)
    async def alternative_titles(self, **kwargs): return await self._get("/alternative_titles", **kwargs)
    async def content_ratings(self, **kwargs): return await self._get("/content_ratings", **kwargs)
    async def credits(self, **kwargs): return await self._get("/credits", **kwargs)
    async def external_ids(self, **kwargs): return await self._get("/external_ids", **kwargs)
    async def images(self, **kwargs): return await self._get("/images", **kwargs)
    async def keywords(self, **kwargs): return await self._get("/keywords", **kwargs)
    async def recommendations(self, **kwargs): return await self._get("/recommendations", **kwargs)
    async def screened_theatrically(self, **kwargs): return await self._get("/screened_theatrically", **kwargs)
    async def similar(self, **kwargs): return await self._get("/similar", **kwargs)
    async def translations(self, **kwargs): return await self._get("/translations", **kwargs)
    async def videos(self, **kwargs): return await self._get("/videos", **kwargs)
    async def watch_providers(self, **kwargs): return await self._get("/watch/providers", **kwargs)

class Season(_Resource):
    def __init__(self, client, tv_id: int, season_number: int): 
        super().__init__(client, ["tv", tv_id, "season", season_number])
        self.tv_id, self.season_number = tv_id, season_number
    def episode(self, episode_number: int): return Episode(self._client, self.tv_id, self.season_number, episode_number)
    async def details(self, **kwargs): return await self._get(**kwargs)
    async def aggregate_credits(self, **kwargs): return await self._get("/aggregate_credits", **kwargs)
    async def credits(self, **kwargs): return await self._get("/credits", **kwargs)
    async def external_ids(self, **kwargs): return await self._get("/external_ids", **kwargs)
    async def images(self, **kwargs): return await self._get("/images", **kwargs)
    async def translations(self, **kwargs): return await self._get("/translations", **kwargs)
    async def videos(self, **kwargs): return await self._get("/videos", **kwargs)

class Episode(_Resource):
    def __init__(self, client, tv_id: int, season_number: int, episode_number: int): 
        super().__init__(client, ["tv", tv_id, "season", season_number, "episode", episode_number])
    async def details(self, **kwargs): return await self._get(**kwargs)
    async def credits(self, **kwargs): return await self._get("/credits", **kwargs)
    async def external_ids(self, **kwargs): return await self._get("/external_ids", **kwargs)
    async def images(self, **kwargs): return await self._get("/images", **kwargs)
    async def translations(self, **kwargs): return await self._get("/translations", **kwargs)
    async def videos(self, **kwargs): return await self._get("/videos", **kwargs)

class Person(_Resource):
    def __init__(self, client, person_id: int): super().__init__(client, ["person", person_id])
    async def details(self, **kwargs): return await self._get(**kwargs)
    async def movie_credits(self, **kwargs): return await self._get("/movie_credits", **kwargs)
    async def tv_credits(self, **kwargs): return await self._get("/tv_credits", **kwargs)
    async def combined_credits(self, **kwargs): return await self._get("/combined_credits", **kwargs)
    async def external_ids(self, **kwargs): return await self._get("/external_ids", **kwargs)
    async def images(self, **kwargs): return await self._get("/images", **kwargs)
    async def translations(self, **kwargs): return await self._get("/translations", **kwargs)

class Collection(_Resource):
    def __init__(self, client, collection_id: int): super().__init__(client, ["collection", collection_id])
    async def details(self, **kwargs): return await self._get(**kwargs)
    async def images(self, **kwargs): return await self._get("/images", **kwargs)
    async def translations(self, **kwargs): return await self._get("/translations", **kwargs)

class Company(_Resource):
    def __init__(self, client, company_id: int): super().__init__(client, ["company", company_id])
    async def details(self, **kwargs): return await self._get(**kwargs)
    async def alternative_names(self, **kwargs): return await self._get("/alternative_names", **kwargs)
    async def images(self, **kwargs): return await self._get("/images", **kwargs)

class Network(_Resource):
    def __init__(self, client, network_id: int): super().__init__(client, ["network", network_id])
    async def details(self, **kwargs): return await self._get(**kwargs)
    async def alternative_names(self, **kwargs): return await self._get("/alternative_names", **kwargs)
    async def images(self, **kwargs): return await self._get("/images", **kwargs)

class Keyword(_Resource):
    def __init__(self, client, keyword_id: int): super().__init__(client, ["keyword", keyword_id])
    async def details(self, **kwargs): return await self._get(**kwargs)
    async def movies(self, **kwargs): return await self._get("/movies", **kwargs)

class Review(_Resource):
    def __init__(self, client, review_id: str): super().__init__(client, ["review", review_id])
    async def details(self, **kwargs): return await self._get(**kwargs)

class Credit(_Resource):
    def __init__(self, client, credit_id: str): super().__init__(client, ["credit", credit_id])
    async def details(self, **kwargs): return await self._get(**kwargs)

class Find(_Resource):
    def __init__(self, client, external_id: str): super().__init__(client, ["find", external_id])
    async def by(self, source: str = "imdb_id", **kwargs): 
        kwargs['external_source'] = source
        return await self._get(**kwargs)

class Discover(_Resource):
    def __init__(self, client): super().__init__(client, ["discover"])
    async def movie(self, **kwargs): return await self._get("/movie", **kwargs)
    async def tv(self, **kwargs): return await self._get("/tv", **kwargs)

class Search(_Resource):
    def __init__(self, client): super().__init__(client, ["search"])
    async def movie(self, query: str, **kwargs): kwargs['query']=query; return await self._get("/movie", **kwargs)
    async def tv(self, query: str, **kwargs): kwargs['query']=query; return await self._get("/tv", **kwargs)
    async def person(self, query: str, **kwargs): kwargs['query']=query; return await self._get("/person", **kwargs)
    async def company(self, query: str, **kwargs): kwargs['query']=query; return await self._get("/company", **kwargs)
    async def collection(self, query: str, **kwargs): kwargs['query']=query; return await self._get("/collection", **kwargs)
    async def keyword(self, query: str, **kwargs): kwargs['query']=query; return await self._get("/keyword", **kwargs)
    async def multi(self, query: str, **kwargs): kwargs['query']=query; return await self._get("/multi", **kwargs)

class Trending(_Resource):
    def __init__(self, client): super().__init__(client, ["trending"])
    async def all(self, time_window: Literal["day", "week"] = "day"): return await self._get(f"/all/{time_window}")
    async def movie(self, time_window: Literal["day", "week"] = "day"): return await self._get(f"/movie/{time_window}")
    async def tv(self, time_window: Literal["day", "week"] = "day"): return await self._get(f"/tv/{time_window}")
    async def person(self, time_window: Literal["day", "week"] = "day"): return await self._get(f"/person/{time_window}")

class Genre(_Resource):
    def __init__(self, client): super().__init__(client, ["genre"])
    async def movie_list(self, **kwargs): return await self._get("/movie/list", **kwargs)
    async def tv_list(self, **kwargs): return await self._get("/tv/list", **kwargs)

class Configuration(_Resource):
    def __init__(self, client): super().__init__(client, ["configuration"])
    async def api_details(self): return await self._get()
    async def countries(self): return await self._get("/countries")
    async def jobs(self): return await self._get("/jobs")
    async def languages(self): return await self._get("/languages")
    async def primary_translations(self): return await self._get("/primary_translations")
    async def timezones(self): return await self._get("/timezones")

class Certification(_Resource):
    def __init__(self, client): super().__init__(client, ["certification"])
    async def movie_list(self): return await self._get("/movie/list")
    async def tv_list(self): return await self._get("/tv/list")
