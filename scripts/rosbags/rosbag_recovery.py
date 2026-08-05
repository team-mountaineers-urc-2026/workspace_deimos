#!/usr/bin/env python3
import yaml
import sqlite3
import collections
import sys
from os import path

# ASSUMPTIONS MADE
# - THE BAG IS NOT COMPRESSED
# - THERE IS ONLY ONE FILE IN THE BAG

class Topic():
    def __init__(self):
        self.name = ""
        self.type = ""
        self.serialization_format = ""
        self.offered_qos_profiles = ""
        self.message_count = 0

class Recoverer():
    def __init__(self):
        self.duration_nanoseconds = False
        self.startingtime_nanoseconds = False
        self.total_message_count = False
        self.topics = []
        self.filepath = False

    def parse_from_sql(self, filepath):

        self.filepath = path.abspath(filepath)

        # Create connection to the database and a cursor
        conn = sqlite3.connect(self.filepath)
        cur = conn.cursor()

        # Get the data for each topic
        cur.execute("SELECT * FROM topics;")
        topic_data = cur.fetchall()

        # Get the data for the messages
        cur.execute("SELECT * FROM messages;")
        message_data = cur.fetchall()

        conn.close()

        # Extract the necessary data
        self.startingtime_nanoseconds = message_data[0][2]
        self.duration_nanoseconds = message_data[-1][2] - message_data[0][2]
        self.total_message_count = message_data[-1][0]

        id_counter = collections.Counter([message[1] for message in message_data])
        id_freqs = dict(id_counter)

        # For each topic recorded in the .db3 file
        for topic in topic_data:
            new_topic = Topic()

            # Parse the data for each topic
            new_topic.name = topic[1]
            new_topic.type = topic[2]
            new_topic.serialization_format = topic[3]
            new_topic.offered_qos_profiles = topic[4]
            new_topic.message_count = id_freqs[topic[0]]

            # Add it to the list
            self.topics.append(new_topic)

    def generate_yaml(self):
        
        # Generate the listing of topics
        topic_list = []
        for topic in self.topics:
            topic_data = {
                'topic_metadata' : {
                    'name' : topic.name,
                    'type' : topic.type,
                    'serialization_format' : topic.serialization_format,
                    'offered_qos_profiles' : topic.offered_qos_profiles
                },
                'message_count' : topic.message_count
            }
            topic_list.append(topic_data)
        
        # Fill in the data
        metadata = {
            'rosbag2_bagfile_information': {
                'version' : 5,
                'storage_identifier' : 'sqlite3',
                'duration' : {
                    'nanoseconds' : self.duration_nanoseconds
                },
                'starting_time' : {
                    'nanoseconds_since_epoch' : self.startingtime_nanoseconds
                },
                'message_count' : self.total_message_count,
                'topics_with_message_count' : 
                    topic_list
                ,
                'compression_format' : "",
                'compression_mode' : "",
                'relative_file_paths' : [
                    path.basename(self.filepath)
                ],
                'files' : [
                    {
                        'path' : path.basename(self.filepath),
                        'starting_time' : {
                            'nanoseconds_since_epoch' : self.startingtime_nanoseconds
                        },
                        'duration' : {
                            'nanoseconds' : self.duration_nanoseconds
                        },
                        'message_count' : self.total_message_count
                    }
                ]
            }
        }

        metadata_as_yaml = yaml.dump(metadata, sort_keys=False)

        # Write the yaml file
        yaml_loc = path.dirname(self.filepath)
        metafile = open(f"{yaml_loc}/metadata.yaml", 'w+')
        metafile.write(metadata_as_yaml)
        metafile.close

def main():
    print('By providing this program the path to a .db3 file, it will create (or overwrite) an appropriate metadata.yaml file in the same directory')
    if not len(sys.argv) == 2:
        print("Incorrect number of arguments, exactly 1 argument must be provided")
        exit(1)

    # Check if the passed path exists
    if not path.exists(sys.argv[1]):
        raise Exception("Given file does not exist")

    recoverer = Recoverer()
    recoverer.parse_from_sql('/home/jdb3/rosbags/rosbag2_2025_02_16-15_14_48/rosbag2_2025_02_16-15_14_48_0.db3')
    recoverer.generate_yaml()

if __name__ == "__main__":
    main()
