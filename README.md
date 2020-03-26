# Voronoi Image Stippling
 Converts a .png or .jpg image into a set of discrete points through an application of [Voronoi Regions](https://www.sciencedirect.com/topics/engineering/voronoi-region)
 
 Using a modified version of Lloyd's algorithm for image stippling known as [Weighted Linde-Buzo-Gray Stippling](http://kops.uni-konstanz.de/bitstream/handle/123456789/41075/Deussen_2-gu29mv4u87jh2.pdf;jsessionid=59CE5E51DFC411DD78F6603DB301C8DF?sequence=1), darker regions in the source image translate into regions with higher densities of stipples.

[Stippling Visualization](https://media.giphy.com/media/Qx5M3UWdhifXn8lZx7/giphy.gif)

## Trying the Program
 Ensure that the following libraries are installed along with a distribution of Python3:
 * OpenCV
 * NumPy
 * PIL
 
 Specify path for source image as well as a target number of stipples.
 
 Adjusting the bounds for target densities (ubound and lbound) will provide different degrees of stipple densities and clustering, to varying results. I have found that the default values work rather well for most images.
   
 The program works best with high-contrast images, adjusting contrast in image-processing software prior to using the stippler will lead to a clearer result.
 
 Currently working on optimizing the program more, since the image initialization step is very slow. It is recommended to keep images smaller than 800x800 pixels
  
  
  
