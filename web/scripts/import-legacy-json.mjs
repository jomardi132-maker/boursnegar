import fs from'node:fs';import pg from'pg';import dotenv from'dotenv';dotenv.config();
const file=process.argv[2];if(!file)throw new Error('db.json path is required');
const parsed=JSON.parse(fs.readFileSync(file,'utf8'));const analyses=Array.isArray(parsed.analyses)?parsed.analyses:[];
const pool=new pg.Pool({host:process.env.DB_HOST,port:Number(process.env.DB_PORT||5432),database:process.env.DB_NAME,user:process.env.DB_USER,password:process.env.DB_PASSWORD});
const client=await pool.connect();let imported=0;
try{await client.query('BEGIN');for(const item of analyses){if(!item?.id||!item?.symbol||!item?.data)continue;const result=await client.query(`INSERT INTO legacy_analysis_imports(legacy_id,legacy_user_id,symbol,report_mode,result,legacy_created_at) VALUES($1,$2,$3,$4,$5,$6) ON CONFLICT(legacy_id) DO NOTHING`,[String(item.id),item.userId?String(item.userId):null,String(item.symbol).slice(0,32),'audited',item.data,item.createdAt||null]);imported+=result.rowCount||0;}await client.query('COMMIT');console.log(JSON.stringify({sourceAnalyses:analyses.length,imported}));}catch(error){await client.query('ROLLBACK');throw error;}finally{client.release();await pool.end();}
