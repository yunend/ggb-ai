# GGB-AI 压缩命令表

实施阶段按需读取。命令中不能混用属性（不同命令的参数签名必须匹配本表）。

## 目录
1. [几何与圆锥曲线](#1-几何与圆锥曲线geometry--conics)
2. [代数与函数](#2-代数与函数algebra--functions)
3. [变换](#3-变换transformations)
4. [列表、向量与序列](#4-列表向量与序列list-vector--sequence)
5. [界面与脚本驱动](#5-界面与脚本驱动ui--scripting)

## 1. 几何与圆锥曲线（Geometry & Conics）
- Angle|3D: ( vec, vec ); ( li, li ); ( pt, ap, pt ); ( pt, pt, pt )
- AngleBisector|Geometry: ( li, li ); ( pt, pt, pt )
- Arc|Geometry: ( cir, pt, pt ); ( ell, pt, pt )
- Area|Geometry: ( pol ); ( co )
- Centroid|Geometry: ( pol )
- Circle|Geometry: ( pt, ra ); ( pt, se ); ( pt, pt ); ( pt, pt, pt )
- CircularArc|Geometry: ( mid, pt, pt )
- CircularSector|Geometry: ( mid, pt, pt )
- Circumcircle|Geometry: ( pt, pt, pt )
- Circumference|Geometry: ( co )
- ClosestPoint|Geometry: ( pat, pt )
- Conic|Geometry: ( pt, pt, pt, pt, pt ); ( n, n, n, n, n, n )
- Directrix|Conic: ( co )
- Distance|Geometry: ( pt, obj ); ( li, li )
- Eccentricity|Conic: ( co )
- Ellipse|Conic: ( fo, fo, sem ax len ); ( fo, fo, pt )
- Focus|Conic: ( co )
- Hyperbola|Conic: ( fo, fo, sem ax len ); ( fo, fo, pt )
- Incircle|Geometry: ( pt, pt, pt )
- Intersect|Geometry: ( obj, obj ); ( obj, obj, in ); ( f, f, st x, End x )
- IntersectPath|Geometry: ( li, pol ); ( pol, pol )
- Line|Geometry: ( pt, pt ); ( pt, par li ); ( pt, di vec )
- Locus|Geometry: ( pt, sl )
- Midpoint|Geometry: ( se ); ( co ); ( pt, pt )
- Parabola|Conic: ( pt, li )
- Perimeter|Geometry: ( pol ); ( co )
- PerpendicularBisector|Geometry: ( se ); ( pt, pt )
- PerpendicularLine|Geometry: ( pt, li ); ( pt, se ); ( pt, pl )
- Point|Geometry: ( obj ); ( obj, pa ); ( pt, vec )
- PointIn|Geometry: ( re )
- Polygon|Geometry: ( pt, …, pt ); ( pt, pt, n ); ( lst )
- Polyline|Geometry: ( pt, …, pt )
- Radius|Geometry: ( co )
- Ray|Geometry: ( st pt, pt ); ( st pt, di vec )
- Segment|Geometry: ( pt, pt ); ( pt, len )
- Semicircle|Geometry: ( pt, pt )
- Sphere|Geometry: ( ce, pt ); ( pt, ra )
- Slope|Geometry: ( li )
- Tangent|Geometry: ( pt, co ); ( pt, f ); ( li, co )
- Vertex|Geometry: ( co ); ( pol ); ( ine )

## 2. 代数与函数（Algebra & Functions）
- Coefficients|Algebra: ( poly )
- CompleteSquare|Algebra: ( qua f )
- Degree|Algebra: ( poly )
- Denominator|Algebra: ( f ); ( ex )
- Derivative|Algebra: ( f ); ( f, n ); ( f, v )
- Expand|Algebra: ( ex )
- Factor|Algebra: ( poly ); ( n )
- Integral|Algebra: ( f ); ( f, st x, End x ); ( f, f, st x, End x )
- LeftSide|Algebra: ( eq )
- Limit|Algebra: ( f, va )
- Max|Algebra: ( lst ); ( n, n ); ( f, st x, End x )
- Min|Algebra: ( lst ); ( n, n ); ( f, st x, End x )
- Numerator|Algebra: ( f ); ( ex )
- PartialFractions|Algebra: ( f )
- Polynomial|Algebra: ( f ); ( lst of po )
- RightSide|Algebra: ( eq )
- Root|Algebra: ( poly ); ( f, st x, End x )
- Simplify|Algebra: ( f ); ( te )
- Solutions|Algebra: ( eq ); ( lst of equ, lst of var )
- Solve|Algebra: ( eq ); ( lst of equ, lst of var )
- Substitute|Algebra: ( ex, sub lst )

## 3. 变换（Transformations）
- Dilate|Transformation: ( obj, dil fa, dil ce pt )
- Reflect|Transformation: ( obj, pt ); ( obj, li ); ( obj, pl )
- Rotate|Transformation: ( obj, an, pt )
- Translate|Transformation: ( obj, vec )

## 4. 列表、向量与序列（List, Vector & Sequence）
- Cross|Vector: ( vec, vec )
- Dot|Vector: ( vec, vec )
- Element|List: ( lst, n )
- Sequence|List: ( ex, v, st, End, inc )
- Vector|Vector: ( pt ); ( st pt, End pt )

## 5. 界面与脚本驱动（UI & Scripting）
- SetColor|Scripting: ( obj, "color" ) // eg: color = (1,0,0) // 0-1 RAG
- SetCaption|Scripting: ( obj, te )
- SetLabelMode|Scripting: ( obj, n )
- SetLayer|Scripting: ( obj, lay )
- SetPointSize|Scripting: ( pt, n )
- SetPointStyle|Scripting: ( pt, n )
- SetLineStyle|Scripting: ( li, n )
- SetLineThickness|Scripting: ( obj, n )
- SetPerspective|Scripting: ( text ) //"T"为3D,"G"为作图区,
- SetVisibleInView|Scripting: ( obj, vi n, bool ) // n=1|2
- SetConditionToShowObject(obj,bool)
- SetValue|Scripting: ( obj, obj )
- SetViewDirection|Scripting: ( di )
- Slider|Scripting: ( Min, Max, inc, spe, wi )
- Text|Text: ( obj, pt )
- FormulaText|Text: ( obj, pt )
- ShowLabel|Scripting: ( obj, bool )
- ZoomIn|Scripting: ( fa ); ( fa, ce )
- ZoomOut|Scripting: ( fa ); ( fa, ce )

## 补充：常用表达式函数（数学运算，允许在表达式中组合）
- sqrt, abs, acos, asin, atan, cos, sin, tan, exp, ln, log, floor, ceil, round
- x( pt ), y( pt ), z( pt ) 取坐标分量；abs( vec ) 取向量长度
