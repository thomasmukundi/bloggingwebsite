create schema thebloggers;

use thebloggers;
CREATE TABLE user (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(60) UNIQUE NOT NULL,
    password VARCHAR(1000) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
select * from blog;
select * from user;
update blog set category='Technology' where id=1;
CREATE TABLE blog (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    slug VARCHAR(150) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    blog_image VARCHAR(100),
    category VARCHAR(100),
    view_count INT,
    date_posted DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES user(id)
);


CREATE TABLE blog_meta (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    description VARCHAR(200),
    keywords VARCHAR(200),
    canonical VARCHAR(200),
    blog_id INT,
    FOREIGN KEY (blog_id) REFERENCES blog(id)
);

CREATE TABLE Comment (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    message TEXT,
    read_status BOOLEAN DEFAULT FALSE,
    blogpost_id INT,
    date_posted date,
    FOREIGN KEY (blogpost_id) REFERENCES Blog(id) ON DELETE CASCADE
);

alter table Comment add column date_posted date;
select * from user;


select * from Comment;

use theblogger;

select * from blog;








CREATE TABLE events (
    eventid INT AUTO_INCREMENT PRIMARY KEY,
    event_name VARCHAR(255) NOT NULL,
    event_date DATE NOT NULL,
    start_time TIME NOT NULL,
    venue VARCHAR(255) NOT NULL,
    event_image VARCHAR(255)
);

CREATE TABLE tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    type ENUM('regular', 'vip', 'vvip') NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    available INT NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(eventid)
);


CREATE TABLE tinypesa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    CheckoutRequestID VARCHAR(500) NOT NULL,
    ResultCode VARCHAR(500) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    MpesaReceiptNumber VARCHAR(500),
    PhoneNumber VARCHAR(500) NOT NULL,
    event_id INT NOT NULL,
    ticket_id INT NOT NULL,
    ticket_type ENUM('regular', 'vip', 'vvip') NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(eventid),
    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
);

CREATE TABLE purchases (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    ticket_id INT NOT NULL,
    CheckoutRequestID VARCHAR(500) NOT NULL,
    ResultCode VARCHAR(500) NOT NULL,
    amount VARCHAR(500) NOT NULL,
    MpesaReceiptNumber VARCHAR(500) NOT NULL,
    PhoneNumber VARCHAR(500) NOT NULL,
    ticket_code VARCHAR(255) NOT NULL,
    qr_code_path VARCHAR(255),
    purchase_date DATETIME NOT NULL,
    is_usable BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (event_id) REFERENCES events(eventid),
    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
);


use seroxide2;

CREATE TABLE admin_ (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

select * from admin_;
select * from events;





-- Insert a hypothetical purchase
INSERT INTO purchases (event_id, ticket_id, CheckoutRequestID, ResultCode, amount, MpesaReceiptNumber, PhoneNumber, ticket_code, qr_code_path, purchase_date, is_usable) 
VALUES 
((SELECT eventid FROM events WHERE event_name = 'Sample'), (SELECT ticket_id FROM tickets WHERE event_id = (SELECT eventid FROM events WHERE event_name = 'Sample') AND type = 'regular'), 'CHKREQ12345', '0', '100.00', 'MPESA12345', '0748023691', 'TICKETCODE123', '', NOW(), 1);


select * from purchases;


update purchases set is_usable=1 where event_id=1;