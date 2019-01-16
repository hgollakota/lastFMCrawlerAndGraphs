import urllib.parse
import urllib.request
import json
import pylast
from crawler_abst_api import CrawlerAbstractAPI


class MyAPI (CrawlerAbstractAPI):
    """
    Encapsulates the interactions for the API used in lab.
    There are people and tags. artist is bipartite 0. Tags bipartite 1.

    Variables
    """
	#EDIT THIS TO REFLECT API Information from LastFM account
    API_KEY="f6b5317d9f966c37f7c21bdd########"
    API_SECRET="bbcced560aede1de9fafe65f########"
    username = "CS299_#####"
    password_hash = pylast.md5("######")
    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET, username=username, password_hash=password_hash)
	
	#Comment for which graph to construct
	initTag = '60s'
#	initTag = '70s'
    


    
    def initial_nodes(self):
       
        init_ = []
        init_.append((initTag, self.make_node_tag(initTag, 0)))
        
        init_artists = self.returnTopArtistsByTag(initTag, 40)
        for artist in init_artists:
            init_.append((artist, self.make_node_artist(artist, 0)))

        print("init_" + initTag)
        print(init_)
        print("top artists")
        print(init_artists)
        return init_

    def returnTopArtistsByTag(self, tagName, lim):
        tag = self.network.get_tag(tagName)
        artists = []
        artistDump = tag.get_top_artists(limit=lim)
		artists = [str(artistDump[i][0]) for i in range(len(artistDump))]
        #iterVar = 0
        #while (iterVar < len(artistDump)):
        #    artists.append(str(artistDump[iterVar][0]))
        #    iterVar = iterVar + 1
        return artists

    def returnTopTagsByArtist(self, artistName, lim):
        artist = self.network.get_artist(artistName)
        tags = []
        tagDump = artist.get_top_tags(limit=lim)
        #iterVar = 0
		tags = [str(tagDump[i][0]) for i in range(len(tagDump))]
        #while (iterVar < len(tagDump)):
        #    tags.append(str(tagDump[iterVar][0]))
        #    iterVar = iterVar + 1
        return tags

    def retTopTagsWeight_Artist(self, artistName, lim):
        artist = self.network.get_artist(artistName)
        data = []
        tagDump = artist.get_top_tags(limit=lim)
        #iterVar = 0
		data = [(str(tagDump[i][0]), str(tagDump[i][1])) for i in range(len(tagDump))]
        #while (iterVar < len(tagDump)):
        #    data.append((str(tagDump[iterVar][0]), str(tagDump[iterVar][1])))
        #    iterVar = iterVar + 1
        return data

    def make_node_artist(self, artist, depth):
        """
        Makes a node representing an artist

        Arguments
        id -- the node id (converted to a string)
        artist -- artist's name
        depth -- depth of the search to this point
        graph -- Graph object to add the node to
        """
        nid = self.make_node(0, artist, depth)
        
        #Get playcount for artist
        art = self.network.get_artist(artist)
        playcount = art.get_playcount()
        
        #Add playcount to graph
        self._graph.nodes[nid]['playcount'] = playcount
        return nid

    def make_node_tag(self, tag, depth):
        """
        Makes a node representing a tag

        Arguments
        id -- the node id (converted to a string)
        tag -- the tag string
        depth -- depth of the search to this point
        graph -- Graph object to add the node to
        """
        nid = super().make_node(1, tag, depth)
        return nid

    def execute_artist_query(self, tag):
        """
        Executes the names query and parses the results.

        Arguments
        tag -- a tag

        Returns
        (success flag, data) -- tuple
        success flag -- true if the values were successfully parsed (no errors)
        data -- a list of names that resulted from the query
        """
        try:
            data = self.returnTopArtistsByTag(tag, 10)
            return (True, data)
        except ValueError as e:
            # Usually this means that the API call has failed
            print(e)
            return self._ERROR_RESULT
        except TypeError as e:
            print(e)
            return self._ERROR_RESULT

    def execute_tags_query(self, artist):
        """
        Executes the tags query and parses the results.

        Arguments
        name -- an artist's name

        Returns
        (success flag, data) -- tuple
        success flag -- true if the values were successfully parsed (no errors)
        data -- a list of tags that resulted from the query
        """
        try:
            data = self.returnTopTagsByArtist(artist, 10)
            return (True, data)
        except ValueError as e:
            # Usually this means that the API call has failed
            print(e)
            return self._ERROR_RESULT
        except TypeError as e:
            print(e)
            return self._ERROR_RESULT

    # These are ARTISTS bipartite 0
    def get_child0(self, node, graph, state):
        artist = graph.node[node]['label']
        success, data = self.execute_tags_query(artist)

        if success:
            # Distinguish nodes previously seen from new nodes
            old_tags = [tag for tag in data if state.is_visited(1, tag)]
            new_tags = [tag for tag in data if not (state.is_visited(1, tag))]

            # Get the existing nodes
            old_nodes = [state.visited_node(1, tag) for tag in old_tags]

            # Create the new nodes
            new_depth = graph.node[node]['_depth'] + 1
            new_nodes = [self.make_node_tag(tag, new_depth)
                         for tag in new_tags]
            # Return the dict with the info
            return {'success': True, 'new': new_nodes, 'old': old_nodes}
        else:
            return {'success': False}

    # These are TAGS bipartite 1
    def get_child1(self, node, graph, state):
        tag = graph.nodes[node]['label']
        success, data = self.execute_artist_query(tag)

        if success:
            # Distinguish nodes previously seen from new nodes
            old_artists = [artist for artist in data if state.is_visited(0, artist)]
            new_artists = [artist for artist in data if not (state.is_visited(0, artist))]
            old_nodes = [state.visited_node(0, artist) for artist in old_artists]

            new_depth = graph.node[node]['_depth'] + 1
            new_nodes = [self.make_node_artist(artist, new_depth)
                         for artist in new_artists]
            return {'success': True, 'new': new_nodes, 'old': old_nodes}
        else:
            return {'success': False}

