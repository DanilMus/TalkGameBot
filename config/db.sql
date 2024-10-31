/*
Код для базы данных
Просто скопируй и вставь в СУБД MySQL
*/

-- Создание базы
CREATE DATABASE IF NOT EXISTS talkgamebot_db;
USE talkgamebot_db;
ALTER DATABASE talkgamebot_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; -- устранение проблем с кодировкой

/*
Создание таблиц
*/
-- Таблица с игроками 
CREATE TABLE Gamers (
    id BIGINT PRIMARY KEY, -- id в телеграмме
    created_at DATETIME,
    -- Внутренние]
    username VARCHAR(63) -- тэг просто, чтобы было удобнее идифицировать
);

-- Таблица админов (игроков с повышенными правами)
CREATE TABLE Admins (
    id BIGINT PRIMARY KEY, -- id в телеграмме
    created_at DATETIME,
    -- Внутренние
    username VARCHAR(63) -- все как и выше
);

-- Таблица чатов, куда подключили бота
CREATE TABLE Chats (
    id BIGINT PRIMARY KEY, -- id чата в телеграмме
    created_at DATETIME,
    -- Внутренние
    name VARCHAR(63), -- название чата
    type ENUM("private", "group", "supergroup", "channel") NOT NULL, -- тип чата (приватный, группа, супергруппа, канал)
    num_members INT, -- количество участников в чате
    bot_is_kicked BOOLEAN DEFAULT FALSE-- удалили ли бота из чата
);

-- Таблица игр (во сколько началась игра и во сколько закончилась)
CREATE TABLE Games (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    created_at DATETIME,
    -- Сторонние 
    id_chat BIGINT
    -- Внутренние
    finished_at DATETIME NULL -- время конца игры

    FOREIGN KEY (id_chat) REFERENCES Chats(id)
);

-- Таблица вопросос и действий - главная таблица, это и есть игры по сути
CREATE TABLE Questions_Actions (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    created_at DATETIME,
    -- Сторонние 
    id_admin BIGINT,
    -- Внутренние
    question_or_action BOOLEAN, -- вопрос - 0, действие - 1
    category ENUM("Активность", "Философия", "Гипотетические ситуации", "Мечты и страхи", "Прошлое", "Юмор", "Пошлое", "Кринж") NOT NULL, -- категория задания
    question_action TEXT, -- текст вопроса или действия

    UNIQUE(question_action), -- текст должен быть уникальным, а иначе в чем смысл
    FOREIGN KEY (id_admin) REFERENCES Admins(id) ON DELETE SET NULL
);

-- Таблица для вопросов и действий от игроков, чтобы было веселеее и чтобы можно было брать идеи у них
CREATE TABLE Questions_Actions_From_Gamers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME,
    -- Сторонние 
    id_gamer BIGINT, 
    id_game INT,
    -- Внутренние
    question_action TEXT, -- текст вопроса или действия, тут они уже могут повторяться

    FOREIGN KEY (id_gamer) REFERENCES Gamers(id)
    FOREIGN KEY (id_gamer) REFERENCES Gamers(id)
);

-- Таблица с ответами. Здесь хранится все знания о том, кто ответил, в какой игре, на какой вопрос, что получил за ответ
CREATE TABLE Answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME,
    -- Сторонние 
    id_participant BIGINT,
    id_question_action INT NULL, -- если есть, значит вопрос от системы, иначе вопрос от игрока
    id_question_action_from_gamer INT NULL, -- аналогично тому, что строчкой выше
    -- Внутренниезаносим, когда закончат)
    round INT, -- в какой раунд
    finished_at DATETIME NULL, -- когда закончили
    score INT NULL, -- с каким счетом ответил

    FOREIGN KEY (id_participant) REFERENCES Participants(id),
    FOREIGN KEY (id_question_action) REFERENCES Questions_Actions(id) ON DELETE SET NULL,
    FOREIGN KEY (id_question_action_from_gamer) REFERENCES Questions_Actions_From_Gamers(id) ON DELETE SET NULL
);

-- Таблица с подключениями. Кто куда подлючился и когда отключился.
CREATE TABLE Participants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created_at DATETIME,
    -- Сторонние 
    id_game INT,
    id_gamer BIGINT,

    FOREIGN KEY (id_game) REFERENCES Games(id),
    FOREIGN KEY (id_gamer) REFERENCES Gamers(id)
);

-- Решаем проблему с кодировками, чтобы можно было заносить русскими буквами
ALTER TABLE Questions_Actions CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE Questions_Actions_From_Gamers CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE Gamers CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE Admins CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE Chats CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;