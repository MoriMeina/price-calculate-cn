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

 Date: 23/08/2024 16:32:28
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for city
-- ----------------------------
DROP TABLE IF EXISTS `city`;
CREATE TABLE `city`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cities` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '辖区',
  `with_elect` tinyint(4) NULL DEFAULT 0 COMMENT '是否按照带电费计价',
  `uuid` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '用于表格',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `cities`(`cities`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 0 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Triggers structure for table city
-- ----------------------------
DROP TRIGGER IF EXISTS `uuid-city`;
delimiter ;;
CREATE TRIGGER `uuid-city` BEFORE INSERT ON `city` FOR EACH ROW BEGIN
    SET NEW.uuid = UUID();
END
;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
