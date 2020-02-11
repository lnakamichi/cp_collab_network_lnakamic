CREATE TABLE IF NOT EXISTS cpcollabnet2019.Collaboration2(
    cid INTEGER NOT NULL AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    year YEAR,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (cid)
);

# contains an entry for each individual researcher
CREATE TABLE IF NOT EXISTS cpcollabnet2019.Researchers2(
    rid INTEGER NOT NULL AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    department VARCHAR(50),
    institution VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (rid)
);

# contains an entry for each other on a collaboration
CREATE TABLE IF NOT EXISTS cpcollabnet2019.Authors2(
    cid INTEGER NOT NULL,
    rid INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (cid) REFERENCES Collaboration2 (cid),
    FOREIGN KEY (rid) REFERENCES Researchers2 (rid),
    PRIMARY KEY (cid, rid)
);
