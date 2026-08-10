import type{StockHealthCardData,QuestionCard}from'../src/types';
import{generateRealHealthCard as generateOriginal,UpstreamAnalysisError}from'./realAnalysisAdapter';
export{UpstreamAnalysisError};
const missing=(id:number,title:string,reason:string):QuestionCard=>({id,title,subtitle:'ارزیابی فقط بر پایه داده مستند انجام می‌شود',status:'mid',statusLabel:'نامشخص',mainMetricValue:'داده کافی نیست',comparisonDetail:reason,summaryAnswer:'به‌دلیل کمبود داده قابل استناد، نتیجه‌گیری انجام نشد.'});
export async function generateRealHealthCard(symbol:string,reportMode:'audited'|'latest_codal'):Promise<StockHealthCardData>{
 const data=await generateOriginal(symbol,reportMode);const current=data.questions||[];
 const questions=[
  current.find(q=>q.id===1)||missing(1,'۱) آیا بازده سودآوری از سود بانکی بهتر است؟','بازده سود یا نرخ بانکی مرجع دارای منبع/تاریخ در دسترس نیست.'),
  current.find(q=>q.id===2)||missing(2,'۲) آیا سود اعلام‌شده واقعی و همراه با جریان نقد است؟','صورت جریان نقد قابل استخراج نیست.'),
  current.find(q=>q.id===3)||missing(3,'۳) آیا رشد واقعی شرکت از تورم بیشتر است؟','دو دوره هم‌طول قابل‌مقایسه و نرخ تورم مرجع دارای منبع و تاریخ در دسترس نیست.'),
 ];
 return{...data,questions};
}
