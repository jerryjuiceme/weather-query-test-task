CREATE TRIGGER update_updated_at_user BEFORE
UPDATE ON "user" FOR EACH ROW EXECUTE PROCEDURE updated_at();