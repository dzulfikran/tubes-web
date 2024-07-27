-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 27 Jul 2024 pada 19.10
-- Versi server: 10.4.28-MariaDB
-- Versi PHP: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `not_is`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `detail_transaksi`
--

CREATE TABLE `detail_transaksi` (
  `id` int(11) NOT NULL,
  `transaksi_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `jumlah` int(11) NOT NULL,
  `subtotal` float NOT NULL
) ;

--
-- Dumping data untuk tabel `detail_transaksi`
--

INSERT INTO `detail_transaksi` (`id`, `transaksi_id`, `product_id`, `jumlah`, `subtotal`) VALUES
(1, 1, 1, 24, 84000),
(2, 1, 2, 12, 84000),
(3, 1, 3, 50, 25000),
(4, 1, 6, 6, 90000),
(5, 2, 4, 24, 36000),
(6, 2, 5, 12, 13200),
(7, 3, 1, 2, 10000),
(8, 4, 2, 1, 10000),
(9, 5, 3, 2, 2000),
(10, 6, 4, 1, 2500),
(11, 7, 6, 1, 25000),
(12, 8, 4, 2, 5000),
(13, 9, 3, 3, 3000),
(14, 9, 2, 1, 10000),
(15, 10, 5, 2, 4000),
(16, 11, 4, 1, 2500);

-- --------------------------------------------------------

--
-- Struktur dari tabel `product`
--

CREATE TABLE `product` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text NOT NULL,
  `harga_beli` float NOT NULL,
  `harga_jual` float NOT NULL,
  `stock` int(11) NOT NULL,
  `category` varchar(50) NOT NULL,
  `image` varchar(200) NOT NULL,
  `user_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `product`
--

INSERT INTO `product` (`id`, `name`, `description`, `harga_beli`, `harga_jual`, `stock`, `category`, `image`, `user_id`) VALUES
(1, 'Lego Ninjago', 'Mainan Keren', 3500, 5000, 22, 'Mainan Anak-Anak', 'images.jpeg', 1),
(2, 'Bola Plastik Besar', 'Bola besar', 7000, 10000, 10, 'Mainan Anak-Anak', 'bola_plastik.jpeg', 1),
(3, 'Bola Plastik Kecil', 'Bola Kecil', 500, 1000, 45, 'Mainan Anak-Anak', 'bola_kecil.jpg', 1),
(4, 'Pena Snowman V-1 Semi-Gel Pen', 'Snowman V-1 hadir dengan bentuk dan kemampuan yang berbobot. Dengan tinta anti macet, menulis jadi cepat dan menyenangkan. Miliki pena ini sekarang juga.', 1500, 2500, 20, 'ATK', 'pulpen.jpeg', 1),
(5, 'SPIDOL MARKER SNOWMAN PW-1A', 'Spidol Tahan Lama Untuk Mewarnai atau Bisa Juga Digunakan Sebagai Permanent Marker Untuk Kebutuhan Menulis. Harga Dan Kualitas Terjamin. MERK SNOWMAN ASLI 100% Asli Original', 1100, 2000, 10, 'ATK', 'spidol.jpeg', 1),
(6, 'Mainan Edukasi Anak Donat Susun 10 Jumbo Plus Bebek', 'Ring Donat jumbo terdiri dari susun susun donat warna warni dan di ujung ada bebek, cocok untuk anak belajar berhitung dan mengenal warna ', 15000, 25000, 5, 'Mainan Anak-Anak', 'donat-susun.jpeg', 1);

-- --------------------------------------------------------

--
-- Struktur dari tabel `transaksi`
--

CREATE TABLE `transaksi` (
  `id` int(11) NOT NULL,
  `tanggal` date NOT NULL,
  `total_harga` float NOT NULL,
  `user_id` int(11) NOT NULL,
  `jenis` enum('PENJUALAN','PEMBELIAN') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `transaksi`
--

INSERT INTO `transaksi` (`id`, `tanggal`, `total_harga`, `user_id`, `jenis`) VALUES
(1, '2024-07-22', 283000, 1, 'PEMBELIAN'),
(2, '2024-07-22', 49200, 1, 'PEMBELIAN'),
(3, '2024-07-23', 10000, 1, 'PENJUALAN'),
(4, '2024-07-23', 10000, 1, 'PENJUALAN'),
(5, '2024-07-24', 2000, 1, 'PENJUALAN'),
(6, '2024-07-24', 2500, 1, 'PENJUALAN'),
(7, '2024-07-25', 25000, 1, 'PENJUALAN'),
(8, '2024-07-25', 5000, 1, 'PENJUALAN'),
(9, '2024-07-26', 13000, 1, 'PENJUALAN'),
(10, '2024-07-26', 4000, 1, 'PENJUALAN'),
(11, '2024-07-26', 2500, 1, 'PENJUALAN');

-- --------------------------------------------------------

--
-- Struktur dari tabel `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `nama_pengguna` varchar(100) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(200) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `profile_pic` varchar(200) NOT NULL,
  `role` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `user`
--

INSERT INTO `user` (`id`, `nama_pengguna`, `username`, `password`, `email`, `phone`, `profile_pic`, `role`) VALUES
(1, 'Isman', 'isman', 'scrypt:32768:8:1$ryDJuncJgDDj3VXz$00992a07c0efb179ca0099e8f1b3704cbbc42cc5bb34799b8021118f9195d3c923fbd6213f7b66f95eabaea71ff707e6479c5bfc3c111376fe17051b3393a8dc', 'isman@gmail.com', '085293140984', 'toko_isman.jpg', 'pemilik'),
(2, 'Muhammad Zulfikran', 'dzull', 'scrypt:32768:8:1$fILK9EJEKaYDr75Z$7088d09cfdbb3f995add2b53d3c1176abdf87b62ceb407232bb06f7ecb1b495adc83ac9b4bc94dc9655f705f6285b60b440a923cdc6e9f8de7f70609c2f3392f', 'dzull234@gmail.com', '085534213412', 'alt-pic.jpg', 'karyawan');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `detail_transaksi`
--
ALTER TABLE `detail_transaksi`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_detail_transaksi_product_id` (`product_id`),
  ADD KEY `ix_detail_transaksi_transaksi_id` (`transaksi_id`);

--
-- Indeks untuk tabel `product`
--
ALTER TABLE `product`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indeks untuk tabel `transaksi`
--
ALTER TABLE `transaksi`
  ADD PRIMARY KEY (`id`),
  ADD KEY `ix_transaksi_user_id` (`user_id`);

--
-- Indeks untuk tabel `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `detail_transaksi`
--
ALTER TABLE `detail_transaksi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT untuk tabel `product`
--
ALTER TABLE `product`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT untuk tabel `transaksi`
--
ALTER TABLE `transaksi`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT untuk tabel `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `detail_transaksi`
--
ALTER TABLE `detail_transaksi`
  ADD CONSTRAINT `detail_transaksi_ibfk_1` FOREIGN KEY (`transaksi_id`) REFERENCES `transaksi` (`id`),
  ADD CONSTRAINT `detail_transaksi_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`);

--
-- Ketidakleluasaan untuk tabel `product`
--
ALTER TABLE `product`
  ADD CONSTRAINT `product_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);

--
-- Ketidakleluasaan untuk tabel `transaksi`
--
ALTER TABLE `transaksi`
  ADD CONSTRAINT `transaksi_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
