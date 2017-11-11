ALTER USER 'root'@'localhost' IDENTIFIED BY 'q1w2e3r4';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'q1w2e3r4';

CREATE DATABASE image_match;
USE image_match;

CREATE TABLE `download` (
  `video_id` varchar(45) NOT NULL,
  `host` varchar(45) DEFAULT NULL,
  `container` varchar(45) DEFAULT NULL,
  `entered` datetime DEFAULT CURRENT_TIMESTAMP,
  `started` datetime DEFAULT NULL,
  `completed` datetime DEFAULT NULL,
  `exit_code` smallint(6) DEFAULT NULL,
  `stdout` text,
  `stderr` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `matches` (
  `id` int(11) NOT NULL,
  `video_id` varchar(16) DEFAULT NULL,
  `task_id` int(11) NOT NULL,
  `frame` int(11) DEFAULT NULL,
  `filename` varchar(45) DEFAULT NULL,
  `distance` int(11) DEFAULT NULL,
  `trainIdx` int(11) DEFAULT NULL,
  `queryIdx` int(11) DEFAULT NULL,
  `imgIdx` int(11) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

CREATE TABLE `render` (
  `video_id` varchar(45) NOT NULL,
  `host` varchar(45) DEFAULT NULL,
  `container` varchar(45) DEFAULT NULL,
  `entered` datetime DEFAULT NULL,
  `started` datetime DEFAULT NULL,
  `completed` datetime DEFAULT NULL,
  `exceptions` int(10) UNSIGNED DEFAULT NULL,
  `notes` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `tasks` (
  `task_id` int(10) UNSIGNED NOT NULL,
  `guid` char(36) NOT NULL,
  `video_id` varchar(16) NOT NULL,
  `template` varchar(128) NOT NULL,
  `entered` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `host` varchar(45) DEFAULT NULL,
  `container` varchar(45) DEFAULT NULL,
  `started` datetime DEFAULT NULL,
  `completed` datetime DEFAULT NULL,
  `exceptions` int(11) UNSIGNED DEFAULT NULL,
  `notes` text
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

ALTER TABLE `download`
  ADD PRIMARY KEY (`video_id`);

ALTER TABLE `matches`
  ADD PRIMARY KEY (`id`),
  ADD KEY `request_id` (`task_id`);

ALTER TABLE `render`
  ADD PRIMARY KEY (`video_id`);

ALTER TABLE `tasks`
  ADD PRIMARY KEY (`task_id`),
  ADD UNIQUE KEY `guuid-video_id` (`guid`,`video_id`),
  ADD KEY `guuid` (`guid`);

ALTER TABLE `matches`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `tasks`
  MODIFY `task_id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

INSERT INTO download (video_id) VALUES ('VgK4E6jonVs');
INSERT INTO download (video_id) VALUES ('pEWBV6Ck11g');
