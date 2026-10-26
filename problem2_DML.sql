
USE registration;

INSERT INTO authors (name, country) VALUES
('J.K. Rowling', 'United Kingdom'),
('George Orwell', 'United Kingdom'),
('Naguib Mahfouz', 'Egypt'),
('Agatha Christie', 'United Kingdom'),
('Ahmed Khaled Tawfik', 'Egypt'),
('Paulo Coelho', 'Brazil');

INSERT INTO books (title, price, author_id) VALUES
('Harry Potter', 25.00, 1),
('The Casual Vacancy', 30.00, 1),
('1984', 20.00, 2),
('Animal Farm', 15.00, 2),
('Palace Walk', 22.00, 3),
('Miramar', 18.00, 3),
('Murder on the Orient Express', 28.00, 4),
('And Then There Were None', 24.00, 4),
('Utopia', 35.00, 5),
('The Blue Elephant', 32.00, 5),
('The Alchemist', 27.00, 6),
('Brida', 21.00, 6);
