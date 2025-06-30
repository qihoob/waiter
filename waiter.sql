CREATE TABLE templates (
                           id INT AUTO_INCREMENT PRIMARY KEY,
                           name VARCHAR(255) NOT NULL,          -- 模板名称 (basic, role等)
                           language VARCHAR(50) NOT NULL,       -- 语言 (zh-CN, en-US等)
                           version VARCHAR(20) NOT NULL,        -- 版本号
                           content TEXT NOT NULL,               -- 模板内容
                           is_active BOOLEAN DEFAULT TRUE,      -- 是否激活
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                           UNIQUE (name, language, version)
);

CREATE TABLE template_versions (
                                   id INT AUTO_INCREMENT PRIMARY KEY,
                                   template_id INT NOT NULL,
                                   version VARCHAR(20) NOT NULL,        -- 版本号
                                   content TEXT NOT NULL,               -- 模板内容
                                   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                   FOREIGN KEY (template_id) REFERENCES templates(id)
);
