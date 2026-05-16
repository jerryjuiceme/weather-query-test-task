CREATE TRIGGER update_updated_at_weather BEFORE
UPDATE ON weather_history FOR EACH ROW EXECUTE PROCEDURE updated_at();