#ifndef RVIZ_WAYPOINT_H
#define RVIZ_WAYPOINT_H

#include <rviz/tool.h>

#include <OgreVector3.h>

#include <QCursor>

#include <ros/ros.h>
# include <QObject>
namespace rviz
{
class Arrow;
class DisplayContext;
class StringProperty;
class ViewportMouseEvent;
}

namespace rviz
{
class RvizWaypoint: public rviz::Tool
{
Q_OBJECT
public:
  RvizWaypoint();
  virtual ~RvizWaypoint() {}
  virtual void onInitialize();
  virtual void activate();
  virtual void deactivate();

  virtual int processMouseEvent( ViewportMouseEvent& event );

protected:
  virtual void onPoseSet(double x, double y, double theta);
  Arrow* arrow_;

  enum State
  {
    Position,
    Orientation
  };
  State state_;

  Ogre::Vector3 pos_;

private Q_SLOTS:
  void updateTopic();

private:
  ros::NodeHandle nh_;
  ros::Publisher pub_;

  StringProperty* topic_property_;
};

}
#endif
