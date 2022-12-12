CREATE TABLE IF NOT EXISTS `arxiv_cs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `s2_id` varchar(128) DEFAULT NULL,
  `title` blob,
  `abstract` longblob,
  `authors` mediumtext,
  `venue` varchar(2048) DEFAULT NULL,
  `year` int DEFAULT NULL,
  `n_citations` int DEFAULT NULL,
  `p_name` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `explanation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `model_name` varchar(45) DEFAULT NULL,
  `method_name` varchar(45) DEFAULT NULL,
  `data_set_name` varchar(45) DEFAULT NULL,
  `data_set_group_name` varchar(45) DEFAULT NULL,
  `task_name` varchar(1024) DEFAULT NULL,
  `explanation` longblob,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `image_net_1000` (
  `id` int NOT NULL AUTO_INCREMENT,
  `img_name` varchar(2048) DEFAULT NULL,
  `img_data` longblob,
  `img_group` varchar(45) DEFAULT NULL,
  `img_label` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`)
) ENGINE=InnoDB;