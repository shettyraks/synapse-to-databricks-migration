-- Insert sample calendar data for fiscal year 2024
INSERT INTO inventory.calendar_dim VALUES
-- January 2024 (4 weeks)
('2024-01-01', 2024, 1, 1, 1, '2024-01', '2024-01-01', '2024-01-28', false, false, false, 1, 1, 'Monday', 'January', 'Q1'),
('2024-01-02', 2024, 1, 1, 1, '2024-01', '2024-01-01', '2024-01-28', false, false, false, 1, 2, 'Tuesday', 'January', 'Q1'),
('2024-01-03', 2024, 1, 1, 1, '2024-01', '2024-01-01', '2024-01-28', false, false, false, 1, 3, 'Wednesday', 'January', 'Q1'),
('2024-01-04', 2024, 1, 1, 1, '2024-01', '2024-01-01', '2024-01-28', false, false, false, 1, 4, 'Thursday', 'January', 'Q1'),
('2024-01-05', 2024, 1, 1, 1, '2024-01', '2024-01-01', '2024-01-28', false, false, false, 1, 5, 'Friday', 'January', 'Q1'),
('2024-01-06', 2024, 1, 1, 1, '2024-01', '2024-01-01', '2024-01-28', false, false, false, 1, 6, 'Saturday', 'January', 'Q1'),
('2024-01-07', 2024, 1, 1, 1, '2024-01', '2024-01-01', '2024-01-28', false, false, false, 1, 7, 'Sunday', 'January', 'Q1'),
-- ... (continuing with 4 weeks for January)
('2024-01-28', 2024, 1, 1, 4, '2024-01', '2024-01-01', '2024-01-28', true, false, false, 4, 7, 'Sunday', 'January', 'Q1'),

-- February 2024 (4 weeks)
('2024-01-29', 2024, 1, 2, 5, '2024-02', '2024-01-29', '2024-02-25', false, false, false, 1, 1, 'Monday', 'February', 'Q1'),
-- ... (continuing with 4 weeks for February)
('2024-02-25', 2024, 1, 2, 8, '2024-02', '2024-01-29', '2024-02-25', true, false, false, 4, 7, 'Sunday', 'February', 'Q1'),

-- March 2024 (5 weeks)
('2024-02-26', 2024, 1, 3, 9, '2024-03', '2024-02-26', '2024-03-31', false, false, false, 1, 1, 'Monday', 'March', 'Q1'),
-- ... (continuing with 5 weeks for March)
('2024-03-31', 2024, 1, 3, 13, '2024-03', '2024-02-26', '2024-03-31', true, true, false, 5, 7, 'Sunday', 'March', 'Q1');


