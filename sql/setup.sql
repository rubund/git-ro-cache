
DROP TABLE IF EXISTS `gitroc_lastaccess`;
CREATE TABLE `gitroc_lastaccess` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `git_url` varchar(256) DEFAULT NULL,
  `git_reponame` varchar(256) DEFAULT NULL,
  `git_commit` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

LOCK TABLES `gitroc_lastaccess` WRITE;
UNLOCK TABLES;
