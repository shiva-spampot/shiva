-- SQL file for temporary database

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


--
-- Database: `Temp`
--

-- --------------------------------------------------------

-- Creating database and using it

CREATE DATABASE `Temp` COLLATE=utf8mb4_unicode_ci;
USE `Temp`;

--
-- Table structure for table `attachments`
--

CREATE TABLE IF NOT EXISTS `attachments` (
  `id` int(255) NOT NULL AUTO_INCREMENT,
  `spam_id` varchar(32) NOT NULL COMMENT 'MD5 of spam from spam table, foreign key',
  `file_name` varchar(100) DEFAULT NULL COMMENT 'Name of the attachment file',
  `attach_type` varchar(12) DEFAULT NULL COMMENT 'Could be either inline/attachment',
  `attachment_file_path` mediumtext NOT NULL,
  `attachmentFileMd5` varchar(32) DEFAULT NULL COMMENT 'MD5 of the attachment',
  `date` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT COLLATE=utf8mb4_unicode_ci AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `links`
--

CREATE TABLE IF NOT EXISTS `links` (
  `id` int(255) NOT NULL AUTO_INCREMENT,
  `spam_id` varchar(32) NOT NULL COMMENT 'MD5 of spam from spam table, foreign key',
  `hyperlink` varchar(100) DEFAULT NULL COMMENT 'Hyperlink from the spam',
  `date` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `sensors`
--

CREATE TABLE IF NOT EXISTS `sensors` (
  `id` int(255) NOT NULL AUTO_INCREMENT,
  `spam_id` varchar(32) NOT NULL COMMENT 'MD5 of spam from spam table, foreign key',
  `sensorID` varchar(100) DEFAULT NULL COMMENT 'Sensor where spam was received',
  `date` date NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `spam`
--

CREATE TABLE IF NOT EXISTS `spam` (
  `id` varchar(32) NOT NULL COMMENT 'MD5 of the spam',
  `ssdeep` varchar(120) DEFAULT NULL COMMENT 'SSDeep hash of the mail',
  `to` mediumtext CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `from` varchar(200) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `textMessage` mediumtext CHARACTER SET utf8 COLLATE utf8_unicode_ci COMMENT 'body of spam in text format',
  `htmlMessage` mediumtext CHARACTER SET utf8 COLLATE utf8_unicode_ci COMMENT 'body of spam in html format',
  `subject` varchar(200) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `headers` text NOT NULL COMMENT 'Header of Spam',
  `sourceIP` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT 'IPs from where mail has been received',
  `sensorID` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT 'Shiva sensor id',
  `firstSeen` datetime NOT NULL COMMENT 'First Occurance of Spam',
  `relayCounter` int(11) NOT NULL DEFAULT '0' COMMENT 'Mails Relayed in an hour',
  `relayTime` datetime NOT NULL COMMENT 'date of first relay',
  `totalCounter` int(11) NOT NULL COMMENT 'total count of spam till date',
  `length` int(11) NOT NULL COMMENT 'Length of the spam',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT COLLATE=utf8mb4_unicode_ci;
