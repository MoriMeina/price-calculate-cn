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

 Date: 23/08/2024 16:32:35
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for cost
-- ----------------------------
DROP TABLE IF EXISTS `cost`;
CREATE TABLE `cost`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uuid` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '前端用于分别项目的uuid',
  `city` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '区县',
  `payment` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '支付方式',
  `commit_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '申请单号',
  `unit` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '局点单位',
  `second_unit` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '二级单位',
  `service` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'IRS项目名称',
  `usingfor` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '主机用途',
  `system` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '系统名称',
  `ip` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '私有IP',
  `eip` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '弹性IP',
  `start_time` date NULL DEFAULT NULL COMMENT '开启时间（可不填）',
  `start_bill_time` date NULL DEFAULT NULL COMMENT '计费开始时间',
  `bill_subject` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '计费项目，必须在price表中有才可添加',
  `ssd` int(255) UNSIGNED NULL DEFAULT 0 COMMENT '按照 (x/100)*价格计算',
  `hdd` int(255) UNSIGNED NULL DEFAULT 0 COMMENT '按照 (x/100)*价格计算',
  `rds_storage` int(255) UNSIGNED NULL DEFAULT 0 COMMENT '按照 (x/100)*价格计算',
  `oss_storage` int(255) UNSIGNED NULL DEFAULT 0 COMMENT '按照 (x/1000)*价格计算',
  `add_fee` json NULL COMMENT '额外计费-给信创中间件、数据库用',
  `ischanged` tinyint(1) NULL DEFAULT NULL COMMENT '默认为Null，变配填入1，注销填入0',
  `ischangedtime` datetime NULL DEFAULT NULL COMMENT '变配、注销时间',
  `comment` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '变配、注销注释用',
  PRIMARY KEY (`id`, `bill_subject`) USING BTREE,
  INDEX `subject`(`bill_subject`) USING BTREE,
  INDEX `unit`(`unit`) USING BTREE,
  INDEX `service`(`service`) USING BTREE,
  INDEX `city`(`city`) USING BTREE,
  INDEX `second-unit`(`second_unit`) USING BTREE,
  CONSTRAINT `city` FOREIGN KEY (`city`) REFERENCES `city` (`cities`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `price` FOREIGN KEY (`bill_subject`) REFERENCES `price` (`format`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `second-unit` FOREIGN KEY (`second_unit`) REFERENCES `service` (`second_unit`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `service` FOREIGN KEY (`service`) REFERENCES `service` (`service`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `unit` FOREIGN KEY (`unit`) REFERENCES `service` (`unit`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 0 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Triggers structure for table cost
-- ----------------------------
DROP TRIGGER IF EXISTS `uuid`;
delimiter ;;
CREATE TRIGGER `uuid` BEFORE INSERT ON `cost` FOR EACH ROW BEGIN
    SET NEW.uuid = UUID();
END
;;
delimiter ;

-- ----------------------------
-- Triggers structure for table cost
-- ----------------------------
DROP TRIGGER IF EXISTS `start_bill`;
delimiter ;;
CREATE TRIGGER `start_bill` BEFORE INSERT ON `cost` FOR EACH ROW BEGIN
    -- 判断日期是在15日之前还是之后，直接在条件语句中计算
    IF DAY(NEW.start_time) < 15 THEN
        -- 如果日期在15日之前，则start_bill_time为下月1日
        SET NEW.start_bill_time = DATE_ADD(LAST_DAY(NEW.start_time), INTERVAL 1 DAY);
    ELSE
        -- 如果日期在15日之后，则start_bill_time为下下月1日
        SET NEW.start_bill_time = DATE_ADD(LAST_DAY(DATE_ADD(NEW.start_time, INTERVAL 1 MONTH)), INTERVAL 1 DAY);
    END IF;
END
;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
