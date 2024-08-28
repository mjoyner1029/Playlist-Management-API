from flask import Flask, request, jsonify

# Define Song class
class Song:
    def __init__(self, song_id, name, artist, genre):
        self.song_id = song_id
        self.name = name
        self.artist = artist
        self.genre = genre

    def __repr__(self):
        return f"Song({self.song_id}, '{self.name}', '{self.artist}', '{self.genre}')"

# Define Playlist class
class Playlist:
    def __init__(self, playlist_id, name):
        self.playlist_id = playlist_id
        self.name = name
        self.songs = []

    def add_song(self, song):
        self.songs.append(song)

    def remove_song(self, song_id):
        self.songs = [song for song in self.songs if song.song_id != song_id]

    def get_song(self, song_id):
        for song in self.songs:
            if song.song_id == song_id:
                return song
        return None

    def sort_songs(self, key):
        if key not in ['name', 'artist', 'genre']:
            raise ValueError("Invalid sort key. Choose 'name', 'artist', or 'genre'.")
        self.songs.sort(key=lambda song: getattr(song, key))

    def __repr__(self):
        return f"Playlist({self.playlist_id}, '{self.name}', Songs: {self.songs})"

# Define PlaylistManager class
class PlaylistManager:
    def __init__(self):
        self.songs = {}
        self.playlists = {}

    def create_song(self, song_id, name, artist, genre):
        if song_id in self.songs:
            raise ValueError("Song ID already exists.")
        self.songs[song_id] = Song(song_id, name, artist, genre)

    def update_song(self, song_id, name=None, artist=None, genre=None):
        song = self.songs.get(song_id)
        if not song:
            raise ValueError("Song not found.")
        if name:
            song.name = name
        if artist:
            song.artist = artist
        if genre:
            song.genre = genre

    def delete_song(self, song_id):
        if song_id in self.songs:
            del self.songs[song_id]
        else:
            raise ValueError("Song not found.")

    def search_song(self, name=None, artist=None, genre=None):
        result = []
        for song in self.songs.values():
            if (name and name.lower() in song.name.lower()) or \
               (artist and artist.lower() in song.artist.lower()) or \
               (genre and genre.lower() in song.genre.lower()):
                result.append(song)
        return result

    def create_playlist(self, playlist_id, name):
        if playlist_id in self.playlists:
            raise ValueError("Playlist ID already exists.")
        self.playlists[playlist_id] = Playlist(playlist_id, name)

    def get_playlist(self, playlist_id):
        return self.playlists.get(playlist_id)

    def update_playlist(self, playlist_id, name=None):
        playlist = self.playlists.get(playlist_id)
        if not playlist:
            raise ValueError("Playlist not found.")
        if name:
            playlist.name = name

    def delete_playlist(self, playlist_id):
        if playlist_id in self.playlists:
            del self.playlists[playlist_id]
        else:
            raise ValueError("Playlist not found.")

    def add_song_to_playlist(self, playlist_id, song_id):
        playlist = self.playlists.get(playlist_id)
        song = self.songs.get(song_id)
        if not playlist:
            raise ValueError("Playlist not found.")
        if not song:
            raise ValueError("Song not found.")
        playlist.add_song(song)

    def remove_song_from_playlist(self, playlist_id, song_id):
        playlist = self.playlists.get(playlist_id)
        if not playlist:
            raise ValueError("Playlist not found.")
        playlist.remove_song(song_id)

# Initialize Flask app
app = Flask(__name__)
manager = PlaylistManager()

# Song Endpoints
@app.route('/songs', methods=['POST'])
def create_song():
    data = request.get_json()
    manager.create_song(data['song_id'], data['name'], data['artist'], data['genre'])
    return jsonify({'message': 'Song created successfully.'}), 201

@app.route('/songs/<int:song_id>', methods=['PUT'])
def update_song(song_id):
    data = request.get_json()
    manager.update_song(song_id, name=data.get('name'), artist=data.get('artist'), genre=data.get('genre'))
    return jsonify({'message': 'Song updated successfully.'})

@app.route('/songs/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    manager.delete_song(song_id)
    return jsonify({'message': 'Song deleted successfully.'})

@app.route('/songs/<int:song_id>', methods=['GET'])
def get_song(song_id):
    song = manager.songs.get(song_id)
    if not song:
        return jsonify({'error': 'Song not found.'}), 404
    return jsonify({'song_id': song.song_id, 'name': song.name, 'artist': song.artist, 'genre': song.genre})

@app.route('/songs/search', methods=['GET'])
def search_song():
    name = request.args.get('name')
    artist = request.args.get('artist')
    genre = request.args.get('genre')
    results = manager.search_song(name=name, artist=artist, genre=genre)
    return jsonify([{'song_id': song.song_id, 'name': song.name, 'artist': song.artist, 'genre': song.genre} for song in results])

# Playlist Endpoints
@app.route('/playlists', methods=['POST'])
def create_playlist():
    data = request.get_json()
    manager.create_playlist(data['playlist_id'], data['name'])
    return jsonify({'message': 'Playlist created successfully.'}), 201

@app.route('/playlists/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    playlist = manager.get_playlist(playlist_id)
    if not playlist:
        return jsonify({'error': 'Playlist not found.'}), 404
    return jsonify({'playlist_id': playlist.playlist_id, 'name': playlist.name, 'songs': [{'song_id': song.song_id, 'name': song.name} for song in playlist.songs]})

@app.route('/playlists/<int:playlist_id>', methods=['PUT'])
def update_playlist(playlist_id):
    data = request.get_json()
    manager.update_playlist(playlist_id, name=data.get('name'))
    return jsonify({'message': 'Playlist updated successfully.'})

@app.route('/playlists/<int:playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    manager.delete_playlist(playlist_id)
    return jsonify({'message': 'Playlist deleted successfully.'})

@app.route('/playlists/<int:playlist_id>/add_song', methods=['POST'])
def add_song_to_playlist(playlist_id):
    data = request.get_json()
    manager.add_song_to_playlist(playlist_id, data['song_id'])
    return jsonify({'message': 'Song added to playlist successfully.'})

@app.route('/playlists/<int:playlist_id>/remove_song', methods=['DELETE'])
def remove_song_from_playlist(playlist_id):
    data = request.get_json()
    manager.remove_song_from_playlist(playlist_id, data['song_id'])
    return jsonify({'message': 'Song removed from playlist successfully.'})

@app.route('/playlists/<int:playlist_id>/sort', methods=['POST'])
def sort_playlist(playlist_id):
    data = request.get_json()
    playlist = manager.get_playlist(playlist_id)
    if not playlist:
        return jsonify({'error': 'Playlist not found.'}), 404
    sort_key = data.get('key', 'name')
    playlist.sort_songs(sort_key)
    return jsonify({'message': 'Playlist sorted successfully.'})

if __name__ == '__main__':
    app.run(debug=True)
