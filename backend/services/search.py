# app/search.py
from typing import List, Dict
import heapq
import logging
import os
import pickle

class TrieNode:
    def __init__(self):
        self.children: Dict[str, TrieNode] = {}
        self.is_end = False
        self.topics = {}

class TopicTrie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, topic_title: str, topic_id: int):
        if not topic_title:
            return
        
        logging.info(f"Inserting topic '{topic_title}' with ID {topic_id}")
        node = self.root
        for char in topic_title.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            if not hasattr(node, 'topics'):
                node.topics = {}
            node.topics[topic_id] = True
        node.is_end = True

    # def _collect_all_topics(self, node: TrieNode, result: set):
    #     if node.is_end:
    #         result.update(node.topics)
    #     for child in node.children.values():
    #         self._collect_all_topics(child, result)
    def _collect_all_topics(self, node: TrieNode, result: set):
        if hasattr(node, 'topics') and node.topics:
            result.update(node.topics.keys())
        for child in node.children.values():
            self._collect_all_topics(child, result)
    
    def search(self, query: str) -> List[int]:
        if not query:
            # Return all topics when query is empty
            result = set()
            self._collect_all_topics(self.root, result)
            return list(result)
        
        logging.info(f"Searching for '{query}'")
        
        # Navigate to the node that matches the query prefix
        node = self.root
        for char in query.lower():
            if char not in node.children:
                logging.info(f"Character '{char}' not found in trie")
                return []
            node = node.children[char]
        
        # Collect topics from this node and all its children
        result = set()
        if hasattr(node, 'topics'):
            result.update(node.topics.keys())
        self._collect_all_topics(node, result)
        
        logging.info(f"Found {len(result)} topics for query '{query}': {list(result)}")
        return list(result)

class TopicRanker:
    def __init__(self, max_size=10):
        self.max_size = max_size
        self.topics = {}

    def add_topic(self, topic_id: int, score: float):
        self.topics[topic_id] = score
        if len(self.topics) > self.max_size:
            # Keep only top max_size topics
            self.topics = dict(sorted(self.topics.items(), key=lambda item: item[1], reverse=True)[:self.max_size])

    def get_top_topics(self) -> List[int]:
        return list(self.topics.keys())

# class TopicRanker:
#     def __init__(self, max_size=10):
#         self.max_size = max_size
#         self.heap = []
    
#     def add_topic(self, topic_id: int, score: float):
#         if len(self.heap) < self.max_size:
#             heapq.heappush(self.heap, (score, topic_id))
#         else:
#             heapq.heappushpop(self.heap, (score, topic_id))
    
#     def get_top_topics(self) -> List[int]:
#         return [topic_id for _, topic_id in sorted(self.heap, reverse=True)]

# Initialize TopicTrie with file persistence
class PersistentTopicTrie(TopicTrie):
    def __init__(self, file_path="trie_data.pkl"):
        super().__init__()
        self.file_path = file_path
        self.load()
    
    def insert(self, topic_title, topic_id):
        super().insert(topic_title, topic_id)
        self.save()
    
    def save(self):
        with open(self.file_path, "wb") as f:
            pickle.dump(self.root, f)
        logging.info(f"Saved trie to {self.file_path}")
    
    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "rb") as f:
                    self.root = pickle.load(f)
                logging.info(f"Loaded trie from {self.file_path}")
            except Exception as e:
                logging.error(f"Error loading trie: {str(e)}")

# Then update your initialization:
topic_trie = PersistentTopicTrie()