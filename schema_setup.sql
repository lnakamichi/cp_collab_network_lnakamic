CREATE TABLE cpcollabnet2019.Collaborations2 (
    cid INTEGER NOT NULL AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    year YEAR,
    data_source VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (cid)
);

# contains an entry for each individual researcher
CREATE TABLE cpcollabnet2019.Researchers2 (
    rid INTEGER NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    last_name VARCHAR(50) NOT NULL,
    department VARCHAR(50),
    institution VARCHAR(50),
    ms_id VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (rid)
);

# contains an entry for each other on a collaboration
CREATE TABLE cpcollabnet2019.Authors2 (
    cid INTEGER NOT NULL,
    rid INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (cid) REFERENCES Collaborations2 (cid),
    FOREIGN KEY (rid) REFERENCES Researchers2 (rid),
    PRIMARY KEY (cid, rid)
);
