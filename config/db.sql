/*
Код для базы данных
Просто скопируй и вставь в СУБД MySQL
*/

-- Создание базы
CREATE DATABASE IF NOT EXISTS talkgamebot_db;
USE talkgamebot_db;
ALTER DATABASE talkgamebot_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

/*
Создание таблиц
*/
-- Таблица с игроками 
CREATE TABLE Gamers (
    id BIGINT PRIMARY KEY, -- id в телеграмме
    -- Внутренние
    username VARCHAR(63) -- тэг просто, чтобы было удобнее идифицировать
);

-- Таблица админов (игроков с повышенными правами)
CREATE TABLE Admins (
    id BIGINT PRIMARY KEY, -- id в телеграмме
    -- Внутренние
    username VARCHAR(63) -- все как и выше
);

-- Таблица игр (во сколько началась игра и во сколько закончилась)
CREATE TABLE Games (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    -- Внутренние
    start_time DATETIME, -- время начала игры
    end_time DATETIME NULL -- время конца игры
);

-- Таблица вопросос и действий - главная таблица, это и есть игры по сути
CREATE TABLE Questions_Actions (
    id INT AUTO_INCREMENT PRIMARY KEY, 
    -- Сторонние 
    id_admin BIGINT,
    -- Внутренние
    question_or_action BOOLEAN, -- вопрос - 0, действие - 1
    category VARCHAR(127), -- категория задания
    question_action TEXT, -- текст вопроса или действия

    UNIQUE(question_action), -- текст должен быть уникальным, а иначе в чем смысл
    FOREIGN KEY (id_admin) REFERENCES Admins(id)
);

-- Таблица для вопросов и действий от игроков, чтобы было веселеее и чтобы можно было брать идеи у них
CREATE TABLE Questions_Actions_From_Gamers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    -- Сторонние 
    id_gamer BIGINT, 
    -- Внутренние
    question_action TEXT, -- текст вопроса или действия, тут они уже могут повторяться

    FOREIGN KEY (id_gamer) REFERENCES Gamers(id)
);

-- Таблица с ответами. Здесь хранится все знания о том, кто ответил, в какой игре, на какой вопрос, что получил за ответ
CREATE TABLE Answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    -- Сторонние 
    id_game INT,
    id_gamer BIGINT,
    id_question_action INT NULL, -- если есть, значит вопрос от системы, иначе вопрос от игрока
    id_question_action_from_gamer INT NULL, -- аналогично тому, что строчкой выше
    -- Внутренние
    start_time DATETIME, -- когда начали (просто запоминаем и заносим, когда закончат)
    end_time DATETIME NULL, -- когда закончили
    round INT, -- в какой раунд
    score INT NULL, -- с каким счетом ответил

    FOREIGN KEY (id_game) REFERENCES Games(id),
    FOREIGN KEY (id_gamer) REFERENCES Gamers(id),
    FOREIGN KEY (id_question_action) REFERENCES Questions_Actions(id),
    FOREIGN KEY (id_question_action_from_gamer) REFERENCES Questions_Actions_From_Gamers(id)
);

-- Таблица с подключениями. Кто куда подлючился и когда отключился.
CREATE TABLE Participants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    -- Сторонние 
    id_game INT,
    id_gamer BIGINT,
    -- Внутренние
    connection_time DATETIME, -- время, когда игрок подключается к игре

    FOREIGN KEY (id_game) REFERENCES Games(id),
    FOREIGN KEY (id_gamer) REFERENCES Gamers(id)
);

-- Решаем проблему с кодировками, чтобы можно было заносить русскими буквами
ALTER TABLE Questions_Actions CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE Questions_Actions_From_Gamers CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE Gamers CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE Admins CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;