import { Pool } from 'pg';

const pool = new Pool({
  user: "crypto",
  host: "localhost",
  database: "crypto",
  password: "crypto",
  port: 5432,
});

export const query = (text, params) => pool.query(text, params);