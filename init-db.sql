IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'QuantDB')
BEGIN
    CREATE DATABASE [QuantDB];
    PRINT 'Database QuantDB created';
END
ELSE
BEGIN
    PRINT 'Database QuantDB already exists';
END