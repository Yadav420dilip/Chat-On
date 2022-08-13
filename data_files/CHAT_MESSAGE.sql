-- phpMyAdmin SQL Dump
-- version 4.6.6deb5
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Sep 30, 2019 at 06:54 PM
-- Server version: 10.3.17-MariaDB-0ubuntu0.19.04.1
-- PHP Version: 7.1.16-1+ubuntu16.04.1+deb.sury.org+1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `CHAT_MESSAGE`
--

DELIMITER $$
--
-- Procedures
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `Fetch_Pending_Msg` (IN `recv` INT(10))  NO SQL
    DETERMINISTIC
BEGIN
SELECT `SENDER_ID`,`RECEIVER_ID`,`MESSAGE` FROM `PENDING_MESSAGE`  WHERE `RECEIVER_ID`=recv;
DELETE FROM `PENDING_MESSAGE` WHERE `RECEIVER_ID`=recv;
COMMIT;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `PENDING_MESSAGE`
--

CREATE TABLE `PENDING_MESSAGE` (
  `SENDER_ID` varchar(10) NOT NULL,
  `RECEIVER_ID` varchar(10) NOT NULL,
  `MESSAGE` varchar(255) NOT NULL,
  `DATE` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `USER_INFO`
--

CREATE TABLE `USER_INFO` (
  `USER_NAME` varchar(100) NOT NULL,
  `USER_ID` varchar(15) NOT NULL,
  `Email_id` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `USER_INFO`
--

INSERT INTO `USER_INFO` (`USER_NAME`, `USER_ID`, `Email_id`) VALUES
('Dilip', '123456789', 'dilip123@gmail.com\r\n'),
('Amam Mishra', '147852369', 'amam@gmail.com'),
('Alok', '369852147', 'alok@gmail.com');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `USER_INFO`
--
ALTER TABLE `USER_INFO`
  ADD PRIMARY KEY (`USER_ID`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
