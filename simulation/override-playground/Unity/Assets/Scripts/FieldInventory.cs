using System;
using System.Collections.Generic;

// Override manual v2, Field Overview p8. Ledger only: positions belong to scenarios.
public sealed class FieldInventory {
 public enum Location { Field, Preload, Reserve, PendingLoad, Removed }
 public sealed class Piece {
  public readonly string Id, Kind, Alliance;
  public readonly bool ClearSideUp;
  public Location State { get; internal set; }
  internal readonly Location Initial;
  internal Piece(string id,string kind,string alliance,Location state,bool clear=false){Id=id;Kind=kind;Alliance=alliance;Initial=state;State=state;ClearSideUp=clear;}
 }
 readonly List<Piece> pieces=new List<Piece>();
 readonly Dictionary<string,Piece> byId=new Dictionary<string,Piece>();
 public IReadOnlyList<Piece> Pieces { get {return pieces.AsReadOnly();} }
 public FieldInventory(){
  Add("redBlue",4,"neutral",Location.Field);
  foreach(string side in new[]{"red","blue"}){
   Add(side+"Yellow",8,side,Location.Field);Add(side+"Yellow",2,side,Location.Preload);Add(side+"Yellow",10,side,Location.Reserve);
   Add("yellowYellow",1,side,Location.Reserve);Add("cup",10,side,Location.Reserve);
  }
  Add("yellowYellow",17,"neutral",Location.Field);
  Add("cup",24,"neutral",Location.Field);Add("cup",12,"neutral",Location.Field,true);
 }
 void Add(string kind,int count,string alliance,Location state,bool clear=false){for(int i=0;i<count;i++){var p=new Piece("piece-"+pieces.Count.ToString("D3"),kind,alliance,state,clear);pieces.Add(p);byId.Add(p.Id,p);}}
 public int Count(Location state,string kind=null){int n=0;foreach(var p in pieces)if(p.State==state&&(kind==null||p.Kind==kind))n++;return n;}
 // Reserve before attempting overlap-checked physical insertion. Never consume rejected loads.
 public string BeginLoad(string alliance,string kind){if(alliance!="red"&&alliance!="blue")return null;foreach(var p in pieces)if(p.State==Location.Reserve&&p.Alliance==alliance&&p.Kind==kind){p.State=Location.PendingLoad;return p.Id;}return null;}
 public bool FinishLoad(string id,bool accepted){Piece p;if(id==null||!byId.TryGetValue(id,out p)||p.State!=Location.PendingLoad)return false;p.State=accepted?Location.Field:Location.Reserve;return true;}
 public bool RemoveFromField(string id){Piece p;if(id==null||!byId.TryGetValue(id,out p)||p.State!=Location.Field)return false;p.State=Location.Removed;return true;}
 public void Reset(){foreach(var p in pieces)p.State=p.Initial;}
 public static void ValidateContract(){
  var x=new FieldInventory();Action<bool,string> check=(ok,reason)=>{if(!ok)throw new Exception("Inventory: "+reason);};
  check(x.pieces.Count==119&&x.Count(Location.Field)==73&&x.Count(Location.Preload)==4&&x.Count(Location.Reserve)==42,"official totals");
  int pins=0,cups=0,clear=0;var ids=new HashSet<string>();foreach(var p in x.pieces){check(ids.Add(p.Id),"duplicate ID");if(p.Kind=="cup"){cups++;if(p.State==Location.Field&&p.ClearSideUp)clear++;}else pins++;}
  check(pins==63&&cups==56&&clear==12,"piece/orientation totals");
  string id=x.BeginLoad("red","cup");check(id!=null&&x.Count(Location.PendingLoad)==1,"pending insertion");check(x.FinishLoad(id,false)&&x.Count(Location.Reserve)==42,"rejected insertion returns inventory");check(!x.FinishLoad(id,true),"double completion rejected");
  for(int i=0;i<10;i++){id=x.BeginLoad("red","cup");check(id!=null&&x.FinishLoad(id,true),"accepted load");}
  check(x.BeginLoad("red","cup")==null,"exhausted red supply");check(x.BeginLoad("red","blueYellow")==null,"wrong-alliance pin");
  id=x.BeginLoad("blue","cup");x.Reset();check(!x.FinishLoad(id,true)&&x.Count(Location.Field)==73&&x.Count(Location.Reserve)==42,"reset cancels outstanding insertion");
  id=x.pieces[0].Id;check(x.RemoveFromField(id)&&!x.RemoveFromField(id),"remove once");x.Reset();check(x.Count(Location.Removed)==0,"reset restores removed piece");
 }
}
