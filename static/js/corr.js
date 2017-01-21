function CrossCorrelate(x,y,maxdelay){
   var n = x.length;
   var i,j;
   var mx,my,sx,sy,sxy,denom,r;

   /* Calculate the mean of the two series x[], y[] */
   mx = 0;
   my = 0;   
   for (i=0;i<n;i++) {
      mx += x[i];
      my += y[i];
   }
   mx /= n;
   my /= n;

   /* Calculate the denominator */
   sx = 0;
   sy = 0;
   for (i=0;i<n;i++) {
      sx += (x[i] - mx) * (x[i] - mx);
      sy += (y[i] - my) * (y[i] - my);
   }
   denom = Math.sqrt(sx*sy);

   var corr = [];

   /* Calculate the correlation series */
   for (delay=-maxdelay;delay<maxdelay;delay++) {
      sxy = 0;
      for (i=0;i<n;i++) {
         j = i + delay;
         if (j < 0 || j >= n)
            continue;
         else
            sxy += (x[i] - mx) * (y[j] - my);
      }
      r = sxy / denom;
      corr.push(r);
   }
   return corr;
}
