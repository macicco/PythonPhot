#!/usr/bin/env python
# D. Jones - 2/13/14
"""This code is from the IDL Astronomy Users Library"""
import numpy as np

def rinter(p, x, y, 
           deriv = True, initialize = False,
           ps1d=True):
    """;+
    ; NAME:
    ;      RINTER
    ; PURPOSE:
    ;      Cubic interpolation of an image at a set of reference points.
    ; EXPLANATION:
    ;      This interpolation program is equivalent to using the intrinsic 
    ;      INTERPOLATE() function with CUBIC = -0.5.   However,
    ;      RINTER() has two advantages: (1) one can optionally obtain the 
    ;      X and Y derivatives at the reference points, and (2) if repeated
    ;      interpolation is to be applied to an array, then some values can
    ;      be pre-computed and stored in Common.   RINTER() was originally  
    ;      for use with the DAOPHOT procedures, but can also be used for 
    ;      general cubic interpolation.
    ;
    ; CALLING SEQUENCE:
    ;      Z = RINTER( P, X, Y, [ DFDX, DFDY ] )
    ;               or
    ;      Z = RINTER(P, /INIT)
    ;
    ; INPUTS:                 
    ;      P  - Two dimensional data array, 
    ;      X  - Either an N element vector or an N x M element array,
    ;               containing X subscripts where cubic interpolation is desired.
    ;      Y -  Either an N element vector or an N x M element array, 
    ;               containing Y subscripts where cubic interpolation is desired.
    ;
    ; OUTPUT:
    ;      Z -  Result = interpolated vector or array.  If X and Y are vectors,
    ;              then so is Z, but if X and Y are arrays then Z will be also.
    ;              If P is DOUBLE precision, then so is Z, otherwise Z is REAL.
    ;
    ; OPTIONAL OUTPUT:
    ;      DFDX - Vector or Array, (same size and type as Z), containing the 
    ;               derivatives with respect to X
    ;      DFDY - Array containing derivatives with respect to Y
    ;
    ; OPTIONAL KEYWORD INPUT:
    ;     /INIT - Perform computations associated only with the input array (i.e. 
    ;             not with X and Y) and store in common.    This can save time if
    ;             repeated calls to RINTER are made using the same array.  
    ;        
    ; EXAMPLE:
    ;      suppose P is a 256 x 256 element array and X = FINDGEN(50)/2. + 100.
    ;      and Y = X.  Then Z will be a 50 element array, containing the
    ;      cubic interpolated points.
    ;
    ; SIDE EFFECTS:
    ;      can be time consuming.
    ;
    ; RESTRICTION:
    ;      Interpolation is not possible at positions outside the range of 
    ;       the array (including all negative subscripts), or within 2 pixel
    ;       units of the edge.  No error message is given but values of the 
    ;       output array are meaningless at these positions.
    ;
    ; PROCEDURE:
    ;       invokes CUBIC interpolation algorithm to evaluate each element
    ;       in Z at virtual coordinates contained in X and Y with the data
    ;       in P.                                                          
    ;
    ; COMMON BLOCKS:
    ;       If repeated interpolation of the same array is to occur, then
    ;       one can save time by initializing the common block RINTER.    
    ;
    ; REVISION HISTORY:
    ;       March 1988 written W. Landsman STX Co.
    ;       Checked for IDL Version 2, J. Isensee, September, 1990
    ;       Corrected call to HISTOGRAM, W. Landsman November 1990
    ;       Converted to IDL V5.0   W. Landsman   September 1997
    ;       Fix output derivatives for 2-d inputs, added /INIT W. Landsman May 2000
    ;       
    ;-"""

    reshape_flag = False
    if len(np.shape(x)) > 1:
        reshape_flag = True
        xshape = np.shape(x)
        yshape = np.shape(y)
        x = x.reshape(xshape[0]*xshape[1])
        y = y.reshape(yshape[0]*yshape[1])

    if not ps1d:
        c = np.shape(p)
    else:
        plen = int(np.sqrt(len(p)))
        c = np.array([plen,plen])
    if len(c) != 2:    
        print('Input array (first parameter) must be 2 dimensional')

    if initialize:

     # Don't use SHIFT function to avoid wraparound at the end points
     
        nx = c[1]
        p_1 = p ; p1 = p ; p2 = p
        p_1[0,1] = p[:,0:nx-2]
        p1[0,0] = p[:,1:]
        p2[0,0] = p[:,2:]
        c1 = 0.5*(p1 - p_1)
        c2 = 2.*p1 + p_1 - 0.5*(5.*p + p2)
        c3 = 0.5*(3.*(p-p1) + p2 - p_1)
        init = 1
 
    sx = np.shape(x)
#    npts = sx[len(sx)+2]
#    if c[3] < 4: c[3] = 4     #Make sure output array at least REAL

    i,j = x.astype(int),y.astype(int)
    xdist = x - i  
    ydist = y - j
    x_1 = c[1]*(j-1) + i
    x0 = x_1 + c[1] 
    x1 = x0 + c[1] 
    x2 = x1 + c[1]

    if not initialize: init = 0    #Has COMMON block been initialized?
    
    if not ps1d:
        pshape = np.shape(p)
        p = p.reshape(pshape[0]*pshape[1])
    if init == 0:

        xgood = np.concatenate((x_1,x0,x1,x2))

        num = np.histogram( xgood, range=[0,max(xgood)+2], bins=range(int(max(xgood)+2)))[0]
        xgood = np.where( num >= 1 )[0] 

        # D. Jones - IDL lets you creatively subscript arrays,
        # so I had to add in some extra steps

        if max(xgood) > len(p)-3:
            p_new = np.zeros(max(xgood)+3)
            plen = len(p)
            p_new[0:plen] = p
            p_new[plen:] = p[plen-1]

            c1 = p*0. ; c2 = p*0. ; c3 = p*0.
            c1_new,c2_new,c3_new = \
                np.zeros(max(xgood)+3),np.zeros(max(xgood)+3),np.zeros(max(xgood)+3)
            clen = len(c1)
            c1_new[0:clen],c2_new[0:clen],c3_new[0:clen] = c1,c2,c3
            c1_new[clen:],c2_new[clen:],c3_new[clen:] = \
                c1[clen-1],c2[clen-1],c3[clen-1]

            p_1 = p_new[xgood-1] ; p0 = p_new[xgood]
            p1 = p_new[xgood+1] ; p2 = p_new[xgood+2]
            c1_new[xgood] = 0.5*( p1 - p_1)
            c2_new[xgood] = 2.*p1 + p_1 - 0.5*(5.*p0 + p2)
            c3_new[xgood] = 0.5*(3.*(p0 - p1) + p2 - p_1)
            
            x0,x1,x2,x_1 = x0.astype(int),x1.astype(int),x2.astype(int),x_1.astype(int)


            y_1 = xdist*( xdist*( xdist*c3_new[x_1] +c2_new[x_1]) + \
                              c1_new[x_1]) + p_new[x_1]
            y0 =  xdist*( xdist*( xdist*c3_new[x0] +c2_new[x0]) + \
                              c1_new[x0]) + p_new[x0]
            y1 =  xdist*( xdist*( xdist*c3_new[x1] +c2_new[x1]) + \
                              c1_new[x1]) + p_new[x1]
            y2 =  xdist*( xdist*( xdist*c3_new[x2] +c2_new[x2]) + \
                              c1_new[x2]) + p_new[x2]

            if deriv:
 
                dy_1 = xdist*(xdist*c3_new[x_1]*3. + 2.*c2_new[x_1]) + c1_new[x_1]
                dy0  = xdist*(xdist*c3_new[x0 ]*3. + 2.*c2_new[x0]) + c1_new[x0]
                dy1  = xdist*(xdist*c3_new[x1 ]*3. + 2.*c2_new[x1]) + c1_new[x1]
                dy2  = xdist*(xdist*c3_new[x2 ]*3. + 2.*c2_new[x2]) + c1_new[x2]
                d1 = 0.5*(dy1 - dy_1)
                d2 = 2.*dy1 + dy_1 - 0.5*(5.*dy0 +dy2)
                d3 = 0.5*( 3.*( dy0-dy1 ) + dy2 - dy_1)
                dfdx =  ydist*( ydist*( ydist*d3 + d2 ) + d1 ) + dy0
        else:

            p_1 = p[xgood-1] ; p0 = p[xgood]
            p1 = p[xgood+1] ; p2 = p[xgood+2]
            c1 = p*0. ; c2 = p*0. ; c3 = p*0.
            c1[xgood] = 0.5*( p1 - p_1)
            c2[xgood] = 2.*p1 + p_1 - 0.5*(5.*p0 + p2)
            c3[xgood] = 0.5*(3.*(p0 - p1) + p2 - p_1)
            
            x0,x1,x2,x_1 = x0.astype(int),x1.astype(int),x2.astype(int),x_1.astype(int)

            y_1 = xdist*( xdist*( xdist*c3[x_1] +c2[x_1]) + \
                              c1[x_1]) + p[x_1]
            y0 =  xdist*( xdist*( xdist*c3[x0] +c2[x0]) + \
                              c1[x0]) + p[x0]
            y1 =  xdist*( xdist*( xdist*c3[x1] +c2[x1]) + \
                              c1[x1]) + p[x1]
            y2 =  xdist*( xdist*( xdist*c3[x2] +c2[x2]) + \
                              c1[x2]) + p[x2]

            if deriv:
 
                dy_1 = xdist*(xdist*c3[x_1]*3. + 2.*c2[x_1]) + c1[x_1]
                dy0  = xdist*(xdist*c3[x0 ]*3. + 2.*c2[x0]) + c1[x0]
                dy1  = xdist*(xdist*c3[x1 ]*3. + 2.*c2[x1]) + c1[x1]
                dy2  = xdist*(xdist*c3[x2 ]*3. + 2.*c2[x2]) + c1[x2]
                d1 = 0.5*(dy1 - dy_1)
                d2 = 2.*dy1 + dy_1 - 0.5*(5.*dy0 +dy2)
                d3 = 0.5*( 3.*( dy0-dy1 ) + dy2 - dy_1)
                dfdx =  ydist*( ydist*( ydist*d3 + d2 ) + d1 ) + dy0

    d1 = 0.5*(y1 - y_1)
    d2 = 2.*y1 + y_1 - 0.5*(5.*y0 +y2)
    d3 = 0.5*(3.*(y0-y1) + y2 - y_1)
    z =  ydist*(ydist*(ydist*d3 + d2) + d1) + y0  

    if deriv: dfdy = ydist*(ydist*d3*3.+2.*d2) + d1   
 
    if ( len(sx) == 2 ):        #Convert results to 2-D if desired

        z = array(z).reshape(sx[0],sx[1] ) 
        if deriv:      #Create output derivative arrays?
            dfdx = array(dfdx).reshape(sx[1],sx[0])
            dfdy = array(dfdy).reshape(sx[1],sx[0])


    if deriv:
        if not reshape_flag:
            return z,dfdx,dfdy
        else:
            return z.reshape(xshape[0],xshape[1]),dfdx,dfdy
    else:
        if not reshape_flag:
            return z
        else:
            return z.reshape(xshape[0],xshape[1])
