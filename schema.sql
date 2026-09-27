-- =========================================================
-- TaskFlow Database Schema
-- Database Name: `todo-application`
-- Engine: InnoDB
-- Character Set: utf8mb4 / Collation: utf8mb4_unicode_ci
-- =========================================================

CREATE DATABASE IF NOT EXISTS `todo-application`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE `todo-application`;

/* =========================================================
   1. USERS TABLE
   Stores registered users and authentication information
   ========================================================= */
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(191) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `profile_image` VARCHAR(500) DEFAULT NULL,
    `is_active` TINYINT(1) NOT NULL DEFAULT 1,
    `last_login` DATETIME DEFAULT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_users_email` (`email`),
    INDEX `idx_users_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/* =========================================================
   2. CATEGORIES TABLE
   Stores user-specific task categories
   ========================================================= */
CREATE TABLE IF NOT EXISTS `categories` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT UNSIGNED NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `description` VARCHAR(255) DEFAULT NULL,
    `icon` VARCHAR(100) DEFAULT NULL,
    `color` VARCHAR(20) DEFAULT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_categories_user`
        FOREIGN KEY (`user_id`)
        REFERENCES `users`(`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE KEY `unique_user_category` (`user_id`, `name`),
    INDEX `idx_categories_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/* =========================================================
   3. TASKS TABLE
   Main table containing all tasks
   ========================================================= */
CREATE TABLE IF NOT EXISTS `tasks` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT UNSIGNED NOT NULL,
    `category_id` INT UNSIGNED DEFAULT NULL,
    `title` VARCHAR(255) NOT NULL,
    `description` TEXT DEFAULT NULL,
    `status` ENUM('pending', 'in_progress', 'completed') NOT NULL DEFAULT 'pending',
    `priority` ENUM('low', 'medium', 'high', 'urgent') NOT NULL DEFAULT 'medium',
    `due_date` DATE DEFAULT NULL,
    `due_time` TIME DEFAULT NULL,
    `completed_at` DATETIME DEFAULT NULL,
    `is_important` TINYINT(1) NOT NULL DEFAULT 0,
    `is_archived` TINYINT(1) NOT NULL DEFAULT 0,
    `sort_order` INT NOT NULL DEFAULT 0,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_tasks_user`
        FOREIGN KEY (`user_id`)
        REFERENCES `users`(`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT `fk_tasks_category`
        FOREIGN KEY (`category_id`)
        REFERENCES `categories`(`id`)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    INDEX `idx_tasks_user` (`user_id`),
    INDEX `idx_tasks_category` (`category_id`),
    INDEX `idx_tasks_status` (`status`),
    INDEX `idx_tasks_priority` (`priority`),
    INDEX `idx_tasks_due_date` (`due_date`),
    INDEX `idx_tasks_completed` (`completed_at`),
    INDEX `idx_tasks_important` (`is_important`),
    INDEX `idx_tasks_archived` (`is_archived`),
    INDEX `idx_tasks_user_status` (`user_id`, `status`),
    INDEX `idx_tasks_user_due_date` (`user_id`, `due_date`),
    INDEX `idx_tasks_user_priority` (`user_id`, `priority`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/* =========================================================
   4. TAGS TABLE
   Stores reusable tags belonging to each user
   ========================================================= */
CREATE TABLE IF NOT EXISTS `tags` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT UNSIGNED NOT NULL,
    `name` VARCHAR(100) NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_tags_user`
        FOREIGN KEY (`user_id`)
        REFERENCES `users`(`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE KEY `unique_user_tag` (`user_id`, `name`),
    INDEX `idx_tags_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/* =========================================================
   5. TASK_TAGS TABLE
   Many-to-many relationship: One task can have many tags.
   ========================================================= */
CREATE TABLE IF NOT EXISTS `task_tags` (
    `task_id` INT UNSIGNED NOT NULL,
    `tag_id` INT UNSIGNED NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`task_id`, `tag_id`),
    CONSTRAINT `fk_task_tags_task`
        FOREIGN KEY (`task_id`)
        REFERENCES `tasks`(`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT `fk_task_tags_tag`
        FOREIGN KEY (`tag_id`)
        REFERENCES `tags`(`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX `idx_task_tags_tag` (`tag_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/* =========================================================
   6. TASK REMINDERS TABLE
   Stores optional reminders for tasks
   ========================================================= */
CREATE TABLE IF NOT EXISTS `task_reminders` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `task_id` INT UNSIGNED NOT NULL,
    `user_id` INT UNSIGNED NOT NULL,
    `reminder_at` DATETIME NOT NULL,
    `reminder_type` ENUM('notification', 'email') NOT NULL DEFAULT 'notification',
    `is_sent` TINYINT(1) NOT NULL DEFAULT 0,
    `sent_at` DATETIME DEFAULT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_reminders_task`
        FOREIGN KEY (`task_id`)
        REFERENCES `tasks`(`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT `fk_reminders_user`
        FOREIGN KEY (`user_id`)
        REFERENCES `users`(`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX `idx_reminders_task` (`task_id`),
    INDEX `idx_reminders_user` (`user_id`),
    INDEX `idx_reminders_time` (`reminder_at`),
    INDEX `idx_reminders_sent` (`is_sent`),
    INDEX `idx_pending_reminders` (`reminder_at`, `is_sent`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

/* =========================================================
   7. USER SETTINGS TABLE
   Stores personal application preferences
   ========================================================= */
CREATE TABLE IF NOT EXISTS `user_settings` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT UNSIGNED NOT NULL UNIQUE,
    `theme` ENUM('light', 'dark', 'system') NOT NULL DEFAULT 'light',
    `default_task_priority` ENUM('low', 'medium', 'high', 'urgent') NOT NULL DEFAULT 'medium',
    `default_task_status` ENUM('pending', 'in_progress') NOT NULL DEFAULT 'pending',
    `tasks_per_page` INT UNSIGNED NOT NULL DEFAULT 20,
    `show_completed_tasks` TINYINT(1) NOT NULL DEFAULT 1,
    `email_notifications` TINYINT(1) NOT NULL DEFAULT 1,
    `reminder_notifications` TINYINT(1) NOT NULL DEFAULT 1,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_settings_user`
        FOREIGN KEY (`user_id`)
        REFERENCES `users`(`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
