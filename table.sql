CREATE TABLE IF NOT EXISTS `taobb_urls` (
  `id` int(11) NOT NULL,
  `key` varchar(5) NOT NULL,
  `url` varchar(1024) NOT NULL,
  `access_time` datetime NOT NULL,
  `access_count` int(11) NOT NULL DEFAULT '0',
  `gmt_create` datetime NOT NULL,
  `gmt_modified` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
