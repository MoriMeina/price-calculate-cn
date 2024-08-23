/*
 Navicat Premium Data Transfer

 Source Server         : 数据流库
 Source Server Type    : MySQL
 Source Server Version : 50728 (5.7.28-log)
 Source Host           : 10.11.203.118:3306
 Source Schema         : price-calculate-cn

 Target Server Type    : MySQL
 Target Server Version : 50728 (5.7.28-log)
 File Encoding         : 65001

 Date: 23/08/2024 16:32:55
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for year_version
-- ----------------------------
DROP TABLE IF EXISTS `year_version`;
CREATE TABLE `year_version`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `year_version` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `year_version`(`year_version`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 0 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
