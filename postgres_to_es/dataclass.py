import datetime as dt
import uuid
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Person:
    """Class for representing a person"""
    id: uuid.UUID
    name: str


@dataclass
class Genre:
    """Class for representing a genre"""
    id: uuid.UUID
    name: str


@dataclass
class Filmwork:
    """Class for film presentation"""
    id: uuid.UUID
    title: str
    description: str
    imdb_rating: float
    type: str
    created_at: dt.datetime
    updated_at: dt.datetime
    actors: Optional[List[Person]] = None
    directors: Optional[List[Person]] = None
    writers: Optional[List[Person]] = None
    actors_names: Optional[List[str]] = None
    director: Optional[List[str]] = None
    writers_names: Optional[List[str]] = None
    genre: List[Optional[Genre]] = field(default_factory=list)

    def add_person(self, role: str, person: Person) -> None:
        """Adds characters to the movie according to their role"""
        if role == 'actor':
            if not self.actors:
                self.actors = []
                self.actors_names = []
            if person not in self.actors:
                self.actors.append(person)
                self.actors_names.append(person.name)
        if role == 'director':
            if not self.director:
                self.director = []
                self.directors = []
            if person not in self.directors:
                self.directors.append(person)
                self.director.append(person.name)
        if role == 'writer':
            if not self.writers:
                self.writers = []
                self.writers_names = []
            if person not in self.writers:
                self.writers.append(person)
                self.writers_names.append(person.name)

    def add_genre(self, genre: Genre) -> None:
        """Adds genres"""
        if genre not in self.genre:
            self.genre.append(genre)


@dataclass
class FilmworkStorage:
    """
         Container class for storing Filmwork objects
    """
    objects: List[Optional[Filmwork]] = field(default_factory=list)

    def get_or_append(self, film: Filmwork) -> Filmwork:
        """
            Adds a movie if there is no movie with the same id in the container.
            Otherwise, returns a movie with the same id from the container
         """
        if self.count:
            for item in self.objects:
                if item.id == film.id:
                    return item
        self.objects.append(film)
        return film

    def get_all(self) -> List[Optional[Filmwork]]:
        """Returns all saved movies in the container"""
        return self.objects

    def count(self) -> int:
        """Returns the number of objects in the container"""
        return len(self.objects)

    def clear(self) -> None:
        """Deletes the contents of the container"""
        self.objects.clear()
