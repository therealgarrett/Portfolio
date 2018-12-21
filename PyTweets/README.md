Install Docker and Kibana

  Used for creating a directory for project.
  Used along side Elasticsearch

Using Docker and Kibana

  docker pull nshou/elasticsearch-kibana
  docker run -d -p 9200:9200 -p 5601:5601 nshouelasticsearch-kibana

Installing Pip Dependencies

$ sudo easy_install pip

Installing TextBlob

$ sudo pip install -U textblob
$ python -m textblob.download_corpora

Installing Tweepy

$ pip install tweepy

"""
    CREATE TABLE `PyData` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `screen_name` varchar(128) DEFAULT NULL,
        `created_at` timestamp NULL DEFAULT NULL,
        `location` varchar(30) DEFAULT NULL,
        `text` text,
        PRIMARY KEY (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=56 DEFAULT CHARSET=utf8;
    """
    # schema http://140dev.com/free-twitter-api-source-code-library/twitter-database-server/mysql-database-schema/
    try:
