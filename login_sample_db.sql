-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 01, 2024 at 04:28 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `login_sample_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(4) NOT NULL,
  `email` varchar(20) NOT NULL,
  `password` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `email`, `password`) VALUES
(1, 'admin@gmail.com', 'admin');

-- --------------------------------------------------------

--
-- Table structure for table `books`
--

CREATE TABLE `books` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `author` varchar(255) NOT NULL,
  `image_url` varchar(500) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` bigint(20) NOT NULL,
  `name` varchar(20) NOT NULL,
  `email` varchar(100) NOT NULL,
  `location` varchar(255) NOT NULL,
  `age` int(11) NOT NULL,
  `password` varchar(100) NOT NULL,
  `date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `location`, `age`, `password`, `date`) VALUES
(11, 'Jayaram Dhungana', 'jayaramdhungana104@gmail.com', '', 0, '$2b$12$hCV0a50CFqps6/8BM5HWAuWlm63GMIl7y6tzE.2KbiWOCnt.stUM6', '2024-11-02 03:32:09'),
(14, 'Ram Kumar Timalsina', 'ram@gmail.com', '', 0, '$2b$12$ZY5BpcbWC40.OE0grnIoH.c0h90fPL6nqpfiHCvYgIyfGeZnUmNxy', '2024-11-17 01:49:27'),
(15, 'hero', 'hero@gmail.com', '', 0, '$2b$12$QZs4mopPUsIglh8ct9B.XeRWPqIhdVNCpelaVup6/YQy/Kq733o.G', '2024-11-18 03:56:27'),
(16, 'milena', 'milena@gmail.com', '', 0, '$2b$12$9.SGpL/6CbsYQXCQhmaS/.HLrbSd6DSNf5LZMO3W0WuYYXO1JJYJK', '2024-11-19 13:31:46'),
(17, 'milla ta', 'millata@gmail.com', '', 0, '$2b$12$qtc/IC04yMe3lRg5s9W5neZ9lrK4iR5RgaCiDgRDMxUg96j8JkIlW', '2024-11-19 17:01:25'),
(18, 'Milyo Milyo', 'Milyo@gmail.com', 'kathmandu', 22, '$2b$12$bRhHccmLfWyHV.MYZ0nJ4O84bzZ6prpKTW1BzcUMj.eCRsCu1qSmi', '2024-11-19 17:03:54');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `books`
--
ALTER TABLE `books`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`name`),
  ADD KEY `date` (`date`),
  ADD KEY `user_name` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(4) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `books`
--
ALTER TABLE `books`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
