-- phpMyAdmin SQL Dump
-- version 5.0.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 25, 2020 at 06:53 PM
-- Server version: 8.0.22
-- PHP Version: 7.3.23

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `evidencija_studenata`
--

-- --------------------------------------------------------

--
-- Table structure for table `korisnici`
--

CREATE TABLE `korisnici` (
  `id` int NOT NULL,
  `ime` varchar(100) NOT NULL,
  `prezime` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `lozinka` varchar(100) NOT NULL,
  `rola` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `korisnici`
--

INSERT INTO `korisnici` (`id`, `ime`, `prezime`, `email`, `lozinka`, `rola`) VALUES
(57, 'admin', 'admin', 'admin@mail.com', 'pbkdf2:sha256:150000$mTapGkPV$61a94106eff092d5e16159f685e25e7d075a6161d94345d71798d6f5b25e7161', 'administrator'),
(74, 'Profersor1', 'Profesor1_P', 'profesor1@gmail.com', 'pbkdf2:sha256:150000$o8E3bpAy$b4087ed9dbc03a8ed105e2f64e51798c88512aff22eb4ec9b4ee8371e693fca9', 'profesor'),
(75, 'Profesor2', 'Profesor2_P', 'profesor2@gmail.com', 'pbkdf2:sha256:150000$5BNHux7y$627a403670463c2bdbfb5b1e8bb0325e688b70b154a044eecb1322ffd355b408', 'profesor'),
(76, 'Profesor3', 'Profesor3_P', 'profesor3@gmail.com', 'pbkdf2:sha256:150000$0FqzYTHh$ce8765f6b6b1a26d518e1a063db8fba1efb21da6d5f93df8e94424fa28492a4b', 'profesor'),
(77, 'Martin', 'Stanković', 'martin@gmail.com', 'pbkdf2:sha256:150000$wpYfLdWC$d4f7ffecd36e37fa2a2b995065e267ee158359203b2fcb60d77a78bc16c4b2cb', 'student'),
(78, 'Jovo', 'Savić', 'jovo@gmail.com', 'pbkdf2:sha256:150000$AgPcFtKB$1054235c4836082390058f4a99187758c20c16a26827af9fe6665423c873e35b', 'student'),
(79, 'Tijana', 'Trajković', 'tijana@gmail.com', 'pbkdf2:sha256:150000$nrW8YcB3$417b6f262d916c3b2ef1452474d21a9d60fa7e057c05508619eb20af5207bffb', 'student'),
(80, 'Ana', 'Jovanović', 'ana@gmial.com', 'pbkdf2:sha256:150000$SUnXxOZa$4001335f15ba9639e33e3b41624fec2e1ca1e37a292c10bd3e79f3eda001ad37', 'student'),
(81, 'Kosta', 'Kostic', 'kosta@gmail.com', 'pbkdf2:sha256:150000$6G84uXES$1b77aefbd05aed3cbf134ebfd3532772497b8dc9d9c4ee4a37abbe188681ee05', 'student'),
(82, 'Jovana', 'Marković', 'jovana@gmail.com', 'pbkdf2:sha256:150000$5uOKvV9y$4e26660fe8f051a8bd2c38b2364d0874667ea1924c47c279316bba34351bdb6e', 'student'),
(83, 'Stefan', 'Lukić', 'stefan@gmail.com', 'pbkdf2:sha256:150000$ezCpZkLN$6c9b07bfb35e05e62c60b7309efeaeeeb9484d583006b2d117ac895149d2f204', 'student'),
(84, 'admin2', 'admin2', 'admin2@mail.com', 'pbkdf2:sha256:150000$GeFPGblh$f59d91054e51f32ceb3e579095fb19ff70d9047ebdabd7ea5205bbce5e877169', 'administrator'),
(85, 'Profesor4', 'Profesor4_P', 'profesor4@gmail.com', 'pbkdf2:sha256:150000$8dT1z4NT$02e23ebc18229bca2f4784f4ed4fa000d94835f108b0c5e4f0e915d2a3edf28d', 'profesor');

-- --------------------------------------------------------

--
-- Table structure for table `ocene`
--

CREATE TABLE `ocene` (
  `id` int NOT NULL,
  `student_id` int NOT NULL,
  `predmet_id` int NOT NULL,
  `ocena` smallint NOT NULL,
  `datum` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `ocene`
--

INSERT INTO `ocene` (`id`, `student_id`, `predmet_id`, `ocena`, `datum`) VALUES
(107, 87, 34, 9, '2020-10-10'),
(110, 89, 41, 10, '2020-05-03'),
(159, 101, 54, 7, '2018-01-11'),
(160, 101, 52, 9, '2019-03-01'),
(161, 101, 55, 10, '2020-01-02'),
(162, 101, 61, 10, '2020-03-01'),
(163, 101, 51, 6, '2018-01-04'),
(164, 101, 53, 10, '2019-09-20'),
(165, 101, 56, 9, '2019-03-13'),
(166, 101, 57, 7, '2020-01-06'),
(168, 101, 59, 6, '2020-02-03'),
(169, 101, 60, 10, '2020-01-01'),
(170, 101, 62, 10, '2020-01-02'),
(171, 102, 51, 10, '2020-01-01'),
(172, 102, 50, 10, '2020-02-03'),
(173, 102, 52, 6, '2018-03-01'),
(174, 102, 54, 6, '2018-01-02'),
(175, 101, 58, 10, '2020-02-03'),
(176, 102, 53, 9, '2018-03-01'),
(177, 102, 55, 7, '2019-04-04'),
(178, 102, 56, 10, '2020-01-04'),
(179, 102, 57, 8, '2019-03-12'),
(180, 102, 59, 6, '2020-01-01'),
(181, 102, 58, 6, '2020-06-06'),
(182, 102, 60, 7, '2020-09-21'),
(183, 102, 61, 9, '2020-04-01'),
(184, 103, 50, 6, '2018-01-03'),
(185, 103, 51, 6, '2018-03-21'),
(186, 103, 52, 8, '2018-04-23'),
(187, 103, 53, 8, '2018-08-04'),
(188, 103, 59, 7, '2020-03-10'),
(189, 103, 55, 6, '2019-05-05'),
(190, 103, 54, 6, '2019-11-21'),
(191, 103, 56, 7, '2020-03-01'),
(192, 103, 57, 9, '2020-03-21'),
(193, 103, 58, 10, '2020-05-05'),
(194, 103, 60, 7, '2019-02-10'),
(195, 103, 61, 6, '2020-04-01'),
(196, 104, 50, 10, '2018-01-01'),
(197, 104, 51, 10, '2020-02-01'),
(198, 104, 52, 8, '2018-02-02'),
(199, 104, 53, 10, '2020-08-20'),
(200, 104, 54, 6, '2018-01-06'),
(201, 104, 55, 9, '2019-02-10'),
(202, 104, 56, 7, '2019-04-05'),
(203, 104, 57, 10, '2020-04-01'),
(204, 104, 58, 10, '2020-03-21'),
(205, 105, 50, 6, '2019-01-01'),
(206, 105, 51, 6, '2020-03-01'),
(207, 105, 52, 8, '2019-05-21'),
(208, 105, 53, 7, '2018-08-08'),
(209, 105, 54, 6, '2020-04-02'),
(210, 105, 55, 7, '2020-04-04'),
(211, 105, 56, 9, '2020-05-01'),
(212, 105, 57, 6, '2019-04-01'),
(213, 105, 58, 9, '2020-08-23'),
(214, 105, 59, 6, '2018-03-01'),
(216, 105, 66, 10, '2020-03-02'),
(217, 105, 65, 7, '2020-02-02'),
(218, 106, 50, 7, '2018-01-01'),
(219, 106, 66, 7, '2019-03-02'),
(220, 106, 65, 10, '2020-05-05'),
(221, 106, 51, 10, '2019-01-10'),
(222, 106, 52, 8, '2018-03-01'),
(223, 106, 53, 8, '2019-08-21'),
(224, 106, 54, 6, '2019-01-01'),
(225, 106, 55, 7, '2019-03-02'),
(226, 106, 57, 7, '2020-10-21'),
(227, 106, 56, 10, '2019-05-10'),
(228, 106, 58, 10, '2019-08-21'),
(229, 106, 59, 6, '2020-01-02'),
(230, 107, 50, 10, '2020-01-01'),
(231, 107, 51, 10, '2020-01-02'),
(232, 107, 52, 6, '2020-03-01'),
(233, 107, 53, 10, '2020-01-06'),
(234, 107, 54, 6, '2020-01-10');

-- --------------------------------------------------------

--
-- Table structure for table `predmeti`
--

CREATE TABLE `predmeti` (
  `id` int NOT NULL,
  `sifra` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `naziv` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `godina_studija` smallint NOT NULL,
  `espb` int NOT NULL,
  `obavezni_izborni` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `predmeti`
--

INSERT INTO `predmeti` (`id`, `sifra`, `naziv`, `godina_studija`, `espb`, `obavezni_izborni`) VALUES
(50, '001_alg', 'Algoritmi i strukture podataka', 1, 6, 'obavezni'),
(51, '002_mat1', 'Matematika 1', 1, 6, 'obavezni'),
(52, '003_oet1', 'Osnovi elektrotehnike', 1, 8, 'obavezni'),
(53, '004_pk', 'Poslovne komunikacije', 1, 4, 'izborni'),
(54, '005_fiz', 'Fizika', 1, 6, 'obavezni'),
(55, '006_bp', 'Baze podataka', 2, 6, 'obavezni'),
(56, '007_it', 'Internet tehnologije', 2, 6, 'izborni'),
(57, '008_oop', 'Objektivno orijentisano programiranje', 2, 6, 'obavezni'),
(58, '009_wd', 'Web dizajn', 2, 6, 'izborni'),
(59, '010_mat2', 'Matematika 2', 2, 6, 'obavezni'),
(60, '011_net', 'Net tehnologije', 3, 6, 'obavezni'),
(61, '012_wp', 'Web programiranje', 3, 6, 'izborni'),
(62, '013_kss', 'Klijent-Server sistemi', 3, 6, 'obavezni'),
(63, '014_armk', 'Arhitektura mikro-kontrolera', 3, 6, 'obavezni'),
(64, '015_sf', 'Softversko inžinjerstvo', 3, 8, 'obavezni'),
(65, '016_el1', 'Osnovi elektronike', 2, 6, 'izborni'),
(66, '017_el2', 'Digitalna elektronika', 2, 6, 'obavezni');

-- --------------------------------------------------------

--
-- Table structure for table `studenti`
--

CREATE TABLE `studenti` (
  `id` int NOT NULL,
  `ime` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `ime_roditelja` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `prezime` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `broj_indeksa` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `godina_studija` smallint NOT NULL,
  `jmbg` bigint NOT NULL,
  `datum_rodjenja` date NOT NULL,
  `espb` int NOT NULL,
  `prosek_ocena` float NOT NULL,
  `broj_telefona` varchar(20) NOT NULL,
  `email` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `slika` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `studenti`
--

INSERT INTO `studenti` (`id`, `ime`, `ime_roditelja`, `prezime`, `broj_indeksa`, `godina_studija`, `jmbg`, `datum_rodjenja`, `espb`, `prosek_ocena`, `broj_telefona`, `email`, `slika`) VALUES
(101, 'Martin', 'Joca', 'Stanković', 'rer1', 3, 510999, '1999-10-05', 72, 8.5833, '0181', 'martin@gmail.com', '510999fman.png'),
(102, 'Jovo', 'Steva', 'Savić', 'rer2', 2, 272000, '1996-02-27', 72, 7.8333, '0182', 'jovo@gmail.com', '272000stl.jpg'),
(103, 'Tijana', 'Uroš', 'Trajković', 'rer3', 3, 258998, '1998-08-25', 72, 7.1667, '0183', 'tijana@gmail.com', '2589982b897468353a406c984155472dc9427c--pretty-drawings.jpg'),
(104, 'Ana', 'Ognjen', 'Jovanović', 'rer4', 3, 104000, '2000-04-01', 54, 8.8889, '0184', 'ana@gmial.com', '104000hba.jpg'),
(105, 'Kosta', 'Ivan', 'Kostic', 'sek10', 3, 1312995, '1995-12-13', 72, 7.25, '01855', 'kosta@gmail.com', '1312995skk.png'),
(106, 'Jovana', 'Milan', 'Marković', 'sek55', 3, 803997, '1997-03-08', 72, 8, '01899', 'jovana@mail.com', '0803997tm.jpg'),
(107, 'Stefan', 'Ilija', 'Lukić', 'sek99', 1, 2402999, '1999-02-24', 30, 8.4, '0187722', 'stefan@gmail.com', '2402999christopher-middleton-porguy.jpg');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `korisnici`
--
ALTER TABLE `korisnici`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `ocene`
--
ALTER TABLE `ocene`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `predmeti`
--
ALTER TABLE `predmeti`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `studenti`
--
ALTER TABLE `studenti`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `korisnici`
--
ALTER TABLE `korisnici`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=86;

--
-- AUTO_INCREMENT for table `ocene`
--
ALTER TABLE `ocene`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=235;

--
-- AUTO_INCREMENT for table `predmeti`
--
ALTER TABLE `predmeti`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=67;

--
-- AUTO_INCREMENT for table `studenti`
--
ALTER TABLE `studenti`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=108;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
