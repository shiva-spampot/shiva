
SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

CREATE DATABASE `Hpfeeds` COLLATE=utf8mb4_unicode_ci;
USE `Hpfeeds`;

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `Hpfeeds`
--

-- --------------------------------------------------------

--
-- Table structure for table `attachment`
--

CREATE TABLE IF NOT EXISTS `attachment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `md5` char(32) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `attachment_file_name` varchar(200) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `attachment_file_path` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `attachment_file_type` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `spam_id` char(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `spam_id` (`spam_id`),
  KEY `md5` (`md5`),
  KEY `attachment_file_name` (`attachment_file_name`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci AUTO_INCREMENT=8 ;

-- --------------------------------------------------------

--
-- Table structure for table `inline`
--

CREATE TABLE IF NOT EXISTS `inline` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `md5` char(32) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `inline_file_name` varchar(200) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `inline_file_path` mediumtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `spam_id` char(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `spam_id` (`spam_id`),
  KEY `md5` (`md5`),
  KEY `inline_file_name` (`inline_file_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `ip`
--

CREATE TABLE IF NOT EXISTS `ip` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `sourceIP` varchar(15) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `sourceIP` (`sourceIP`),
  KEY `date` (`date`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

-- --------------------------------------------------------

--
-- Table structure for table `ip_spam`
--

CREATE TABLE IF NOT EXISTS `ip_spam` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ip_id` int(11) NOT NULL,
  `spam_id` char(32) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ip_id` (`ip_id`),
  KEY `spam_id` (`spam_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

-- --------------------------------------------------------

--
-- Table structure for table `links`
--

CREATE TABLE IF NOT EXISTS `links` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `hyperLink` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `spam_id` char(32) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `spam_id` (`spam_id`),
  KEY `hyperLink` (`hyperLink`),
  KEY `date` (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `relay`
--

CREATE TABLE IF NOT EXISTS `relay` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `firstRelayed` datetime NOT NULL COMMENT 'date of first relay',
  `lastRelayed` datetime NOT NULL COMMENT 'date of last relay',
  `totalRelayed` int(11) NOT NULL DEFAULT '0' COMMENT 'Total Mails Relayed Till Date',
  `spam_id` char(32) NOT NULL,
  `sensorID` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `spam_id` (`spam_id`),
  KEY `sensorID` (`sensorID`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

-- --------------------------------------------------------

--
-- Table structure for table `sdate`
--

CREATE TABLE IF NOT EXISTS `sdate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `firstSeen` datetime NOT NULL COMMENT 'First Occurance of Spam',
  `lastSeen` datetime NOT NULL COMMENT 'Last Occurance of Spam',
  `todaysCounter` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `firstSeen` (`firstSeen`),
  KEY `lastSeen` (`lastSeen`),
  KEY `date` (`date`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

-- --------------------------------------------------------

--
-- Table structure for table `sdate_spam`
--

CREATE TABLE IF NOT EXISTS `sdate_spam` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `spam_id` char(64) NOT NULL,
  `date_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `spam_id` (`spam_id`),
  KEY `date_id` (`date_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=5 ;

-- --------------------------------------------------------

--
-- Table structure for table `sensor`
--

CREATE TABLE IF NOT EXISTS `sensor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `sensorID` varchar(50) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT 'Shiva sensor id',
  PRIMARY KEY (`id`),
  KEY `sensorID` (`sensorID`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=4 ;

-- --------------------------------------------------------

--
-- Table structure for table `sensor_spam`
--

CREATE TABLE IF NOT EXISTS `sensor_spam` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sensor_id` int(11) NOT NULL,
  `spam_id` char(32) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `sensor_id` (`sensor_id`),
  KEY `spam_id` (`spam_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=4 ;

-- --------------------------------------------------------

--
-- Table structure for table `spam`
--

CREATE TABLE IF NOT EXISTS `spam` (
  `id` char(32) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Md5 of combination of fields',
  `from` varchar(200) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `subject` varchar(200) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `to` longtext CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `textMessage` mediumtext CHARACTER SET utf8 COLLATE utf8_unicode_ci COMMENT 'body of spam in text format',
  `htmlMessage` mediumtext CHARACTER SET utf8 COLLATE utf8_unicode_ci COMMENT 'body of spam in html format',
  `totalCounter` int(11) NOT NULL COMMENT 'total count of spam till date',
  `ssdeep` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'SSDeep hash of the mail',
  `headers` text COLLATE utf8mb4_unicode_ci NOT NULL COMMENT 'Header of Spam',
  `length` int(11) NOT NULL COMMENT 'Length of the spam',
  PRIMARY KEY (`id`),
  KEY `subject` (`subject`),
  KEY `totalCounter` (`totalCounter`),
  KEY `headers` (`headers`(191)),
  KEY `textMessage` (`textMessage`(255)),
  KEY `htmlMessage` (`htmlMessage`(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
