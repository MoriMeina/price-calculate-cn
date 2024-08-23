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

 Date: 23/08/2024 16:32:42
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for price
-- ----------------------------
DROP TABLE IF EXISTS `price`;
CREATE TABLE `price`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uuid` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `project` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `billing` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `format_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `format` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `price` int(11) NULL DEFAULT NULL,
  `price_with_elect` int(11) NULL DEFAULT NULL,
  `version` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`, `version`) USING BTREE,
  INDEX `format`(`format`) USING BTREE,
  INDEX `year_version`(`version`) USING BTREE,
  CONSTRAINT `year_version` FOREIGN KEY (`version`) REFERENCES `year_version` (`year_version`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 0 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Triggers structure for table price
-- ----------------------------
DROP TRIGGER IF EXISTS `price_uuid`;
delimiter ;;
CREATE TRIGGER `price_uuid` BEFORE INSERT ON `price` FOR EACH ROW BEGIN
    SET NEW.uuid = UUID();
END
;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
