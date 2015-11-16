#pragma once
/****
 *CVAC Software Disclaimer
 *
 *This software was developed at the Naval Postgraduate School, Monterey, CA,
 *by employees of the Federal Government in the course of their official duties.
 *Pursuant to title 17 Section 105 of the United States Code this software
 *is not subject to copyright protection and is in the public domain. It is 
 *an experimental system.  The Naval Postgraduate School assumes no
 *responsibility whatsoever for its use by other parties, and makes
 *no guarantees, expressed or implied, about its quality, reliability, 
 *or any other characteristic.
 *We would appreciate acknowledgement and a brief notification if the software
 *is used.
 *
 *Redistribution and use in source and binary forms, with or without
 *modification, are permitted provided that the following conditions are met:
 *    * Redistributions of source code must retain the above notice,
 *      this list of conditions and the following disclaimer.
 *    * Redistributions in binary form must reproduce the above notice,
 *      this list of conditions and the following disclaimer in the
 *      documentation and/or other materials provided with the distribution.
 *    * Neither the name of the Naval Postgraduate School, nor the name of
 *      the U.S. Government, nor the names of its contributors may be used
 *      to endorse or promote products derived from this software without
 *      specific prior written permission.
 *
 *THIS SOFTWARE IS PROVIDED BY THE NAVAL POSTGRADUATE SCHOOL (NPS) AND CONTRIBUTORS
 *"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 *THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 *ARE DISCLAIMED. IN NO EVENT SHALL NPS OR THE U.S. BE LIABLE FOR ANY
 *DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 *(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 *LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 *ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 *(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 *SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *****/

#include <iomanip>
#include <vector>
#include <opencv2/opencv.hpp>
#include <util/processRunSet.h>
//#pragma comment(lib,"opencv_core245.lib")
//#pragma comment(lib,"opencv_highgui245.lib")
//#pragma comment(lib,"opencv_imgproc245.lib")

namespace cvac
{  
  class MediaConverter
  {
  public:
    MediaConverter(ServiceManager *_sman = NULL);
    ~MediaConverter(){};	
  public:
    ServiceManager* mServiceMan;
  public:
    virtual bool convert(const string& _srcAbsPath,
                         const string& _desAbsDir,
                         const string& _desFilename,
                         vector<string>& _resFilename,
                         vector<string>& _resAuxInfo) = 0;
  };


  class MediaConverter_openCV_i2i : public MediaConverter
  {
  public:
    MediaConverter_openCV_i2i(ServiceManager *_sman = NULL);
    ~MediaConverter_openCV_i2i(){};
  public:
    bool convert(const string& _srcAbsPath,
                 const string& _desAbsDir,
                 const string& _desFilename,
                 vector<string>& _resFilename,
                 vector<string>& _resAuxInfo);
  };

  class ImageMagickConverter_i2i : public MediaConverter
  {
  public:
    ImageMagickConverter_i2i(ServiceManager *_sman = NULL);
    ~ImageMagickConverter_i2i(){};
    bool convert(const string& _srcAbsPath,
                 const string& _desAbsDir,
                 const string& _desFilename,
                 vector<string>& _resFilename,
                 vector<string>& _resAuxInfo);
  };

  class MediaConverter_openCV_v2i : public MediaConverter
  {
  public:
    MediaConverter_openCV_v2i(ServiceManager *_sman = NULL,
                              int _perFrame = -1);
    ~MediaConverter_openCV_v2i();

  private:
    bool checkDuplicateConversion(const string& _srcAbsPath,
                                  const int& _perfrm,
                                  vector<string>& _resFilename,
                                  vector<string>& _resFrameInfo);
    cv::VideoCapture mVideoFile;	
    int PerFrame;
    vector< vector<string> > dupli_Filename;
    vector< vector<string> > dupli_FrameInfo;
    vector<string> dupli_srcPath;
    vector<int> dupli_perFrame;

  public:
    bool convert(const string& _srcAbsPath,
                 const string& _desAbsDir,
                 const string& _desFilename,
                 vector<string>& _resFilename,
                 vector<string>& _resFrameInfo);
  };
}
