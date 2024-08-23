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

 Date: 23/08/2024 16:32:49
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for service
-- ----------------------------
DROP TABLE IF EXISTS `service`;
CREATE TABLE `service`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uuid` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `city` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `unit` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `second_unit` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `service` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `client` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `client_phone` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `unit`(`unit`) USING BTREE,
  INDEX `service`(`service`) USING BTREE,
  INDEX `辖区`(`city`) USING BTREE,
  INDEX `second-unit`(`second_unit`) USING BTREE,
  CONSTRAINT `辖区` FOREIGN KEY (`city`) REFERENCES `city` (`cities`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 0 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Triggers structure for table service
-- ----------------------------
DROP TRIGGER IF EXISTS `service_uuid`;
delimiter ;;
CREATE TRIGGER `service_uuid` BEFORE INSERT ON `service` FOR EACH ROW BEGIN
    SET NEW.uuid = UUID();
END
;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
