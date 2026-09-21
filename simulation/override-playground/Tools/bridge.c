#include <mujoco/mujoco.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
static mjModel*m;static mjData*d;static double liftTarget=-.60, jawTarget=1.047;static double cmdF,cmdT,cmdL,cmdJ,cmdR;
// User-requested faster simulation controls, September 20. Speed targets are
// gameplay estimates, not revised hardware specifications; torque caps unchanged.
static const double controlSpeed=1.5, intakeSpeed=2.0;
static int aids[11],jids[11],liftDofs[6];
static const char*liftNames[]={"lift","lower_parallel","rear_upright","upper_lift","upper_parallel","claw_upright"};
static const double liftSigns[]={1,1,-1,1,1,1};
static const char*names[]={"wheel00","wheel01","wheel02","wheel10","wheel11","wheel12","lift","jawL","jawR","rollerL","rollerR"};
static double clamp(double x,double l,double h){return x<l?l:x>h?h:x;}
int pg_engine_version(){return mj_version();}
void pg_close(){if(d)mj_deleteData(d);if(m)mj_deleteModel(m);d=0;m=0;}
void pg_reset(int scene){
 if(!m)return;mj_resetData(m,d);liftTarget=-.60;jawTarget=1.047;cmdF=cmdT=cmdL=cmdJ=cmdR=0;
 const char*jn[]={"lift","lower_parallel","rear_upright","upper_lift","upper_parallel","claw_upright","jawL","jawR"};
 for(int k=0;k<8;k++){int j=mj_name2id(m,mjOBJ_JOINT,jn[k]);d->qpos[m->jnt_qposadr[j]]=k<6?(k==2?-liftTarget:liftTarget):jawTarget;}
 for(int k=0;k<2;k++){int j=mj_name2id(m,mjOBJ_JOINT,k?"gearSunR":"gearSunL");if(j>=0)d->qpos[m->jnt_qposadr[j]]=0;}
 if(scene==1){for(int i=0;i<18;i++){char n[32];snprintf(n,sizeof(n),i<12?"pin%dfree":"cup%dfree",i<12?i:i-12);int j=mj_name2id(m,mjOBJ_JOINT,n);int q=m->jnt_qposadr[j];d->qpos[q]=((i%5)-2)*.12;d->qpos[q+1]=-.1-(i/5)*.12;d->qpos[q+2]=.10+(i%3)*.07;d->qpos[q+3]=.70710678;d->qpos[q+4]=.70710678;d->qpos[q+5]=d->qpos[q+6]=0;}}
 if(scene==2){for(int i=0;i<3;i++){char n[32];snprintf(n,sizeof(n),"cup%dfree",i);int j=mj_name2id(m,mjOBJ_JOINT,n),q=m->jnt_qposadr[j];d->qpos[q]=.5;d->qpos[q+1]=-.2;d->qpos[q+2]=.003+i*.1645;}int j=mj_name2id(m,mjOBJ_JOINT,"pin0free"),q=m->jnt_qposadr[j];d->qpos[q]=.5;d->qpos[q+1]=-.2;d->qpos[q+2]=.53;}
 if(scene==3){int j=mj_name2id(m,mjOBJ_JOINT,"pin0free"),q=m->jnt_qposadr[j];d->qpos[q]=0;d->qpos[q+1]=.685;d->qpos[q+2]=.003;}
 mj_forward(m,d);
}
int pg_load(const char*p,char*error,int cap){pg_close();m=mj_loadXML(p,0,error,cap);if(!m)return 0;d=mj_makeData(m);for(int k=0;k<11;k++){aids[k]=mj_name2id(m,mjOBJ_ACTUATOR,names[k]);jids[k]=mj_name2id(m,mjOBJ_JOINT,names[k]);}for(int k=0;k<6;k++){int j=mj_name2id(m,mjOBJ_JOINT,liftNames[k]);liftDofs[k]=m->jnt_dofadr[j];}pg_reset(0);return m->nbody;}
void pg_command(double f,double t,double l,double j,double r){cmdF=clamp(f,-1,1);cmdT=clamp(t,-1,1);cmdL=clamp(l,-1,1);cmdJ=clamp(j,-1,1);cmdR=clamp(r,-1,1);}
void pg_step(int count){if(!m)return;for(int z=0;z<count;z++){
 liftTarget=clamp(liftTarget+cmdL*.48*controlSpeed*m->opt.timestep,-.72,.0873);jawTarget=clamp(jawTarget+cmdJ*1.4*controlSpeed*m->opt.timestep,.17453,1.3962634);
 for(int k=0;k<11;k++){
 int j=jids[k];double q=d->qpos[m->jnt_qposadr[j]],v=d->qvel[m->jnt_dofadr[j]],u=0;
 // Adapted from ftcsim Motor.torque (MIT, Research/ftcsim-LICENSE).
 // Provisional 600 RPM V5 cartridge, 60/36 external reduction, 0.8 transmission efficiency.
 // 2.1 Nm is the 100 RPM cartridge: stall at 600 RPM is scaled to 0.35 Nm.
 // Linear voltage/brake approximation; NOT V5 firmware or measured hardware.
 if(k<6){double power=clamp(cmdF+(k<3?cmdT:-cmdT),-1,1);double stall=(2.1/6.0)*(60.0/36.0)*.8;u=clamp(stall*(power-v/(controlSpeed*600*2*M_PI/60/(60.0/36.0))),-stall,stall);
 // Explicit finite-torque active braking at zero input, replacing accidental
 // bearing drag. Gain is an uncalibrated controller estimate, not V5 firmware.
 if(fabs(power)<.0001)u=clamp(-.08*v,-stall,stall);}
 else if(k==6){
 // Project gravity/Coriolis bias onto the coupled lift coordinate (virtual work).
 // Estimated model compensation shares the same finite 22 Nm actuator budget.
 double bias=0;for(int h=0;h<6;h++)bias+=liftSigns[h]*d->qfrc_bias[liftDofs[h]];
 u=clamp(bias+180*(liftTarget-q)-12*v,-22,22);
 }
 else if(k<9)u=clamp(9*(jawTarget-q)-.15*v,-1.2,1.2);
 else u=clamp(((k==9?1:-1)*cmdR*15*intakeSpeed-v)*.012,-.12,.12);
 d->ctrl[aids[k]]=u;
 }mj_step(m,d);
}}
void pg_poses(double*out){if(!d)return;for(int i=0;i<m->nbody;i++){memcpy(out+i*7,d->xpos+i*3,3*sizeof(double));memcpy(out+i*7+3,d->xquat+i*4,4*sizeof(double));}}
int pg_body(const char*n){return m?mj_name2id(m,mjOBJ_BODY,n):-1;}
void pg_status(double*out){if(!d)return;int r=mj_name2id(m,mjOBJ_BODY,"robot");out[0]=d->time;out[1]=d->ncon;out[2]=d->qpos[m->jnt_qposadr[jids[6]]];out[3]=d->qpos[m->jnt_qposadr[jids[7]]];out[4]=d->actuator_force[aids[6]];out[5]=d->xpos[r*3];out[6]=d->xpos[r*3+1];out[7]=d->xpos[r*3+2];out[8]=d->warning[mjWARN_BADQACC].number;out[9]=d->warning[mjWARN_BADQPOS].number;out[10]=liftTarget;out[11]=jawTarget;}
// Fixture setup only: reposition a free game piece before a trial; never attach it.
int pg_place_piece(const char*name,double x,double y,double z){
 if(!m || (strncmp(name,"pin",3)&&strncmp(name,"cup",3)))return 0;
 int b=mj_name2id(m,mjOBJ_BODY,name);if(b<0||m->body_jntnum[b]!=1)return 0;
 int j=m->body_jntadr[b];if(m->jnt_type[j]!=mjJNT_FREE)return 0;
 int q=m->jnt_qposadr[j],v=m->jnt_dofadr[j];d->qpos[q]=x;d->qpos[q+1]=y;d->qpos[q+2]=z;
 d->qpos[q+3]=1;d->qpos[q+4]=d->qpos[q+5]=d->qpos[q+6]=0;for(int k=0;k<6;k++)d->qvel[v+k]=0;
 mj_forward(m,d);return 1;
}

// Read-only contact evidence for diagnostics and future support classification.
// Each record: geom1,geom2,body1,body2,signed separation,normal force (SI).
int pg_contact_evidence(double*out,int capacity){
 if(!m||!d||!out||capacity<=0)return 0;
 int count=d->ncon<capacity?d->ncon:capacity;
 for(int i=0;i<count;i++){mjContact*c=&d->contact[i];mjtNum force[6]={0};mj_contactForce(m,d,i,force);
  out[6*i]=c->geom[0];out[6*i+1]=c->geom[1];out[6*i+2]=m->geom_bodyid[c->geom[0]];out[6*i+3]=m->geom_bodyid[c->geom[1]];out[6*i+4]=c->dist;out[6*i+5]=force[0];
 }return count;
}
