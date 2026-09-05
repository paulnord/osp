package org.opensourcephysics.tools;
import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import org.opensourcephysics.display.Dataset;
public class BrowserFitTest {
 public static DataTool tool;
 public static DataToolTab tab;
 public static DatasetCurveFitter fitter;
 public static void main(String[] args) {
  tool=new DataTool(data(16));tab=tool.getTab(0);tab.checkGUI();fitter=tab.getCurveFitter();
  tab.showFitterAction.actionPerformed(new ActionEvent(tab,0,fitter.getPolyFitNameOfDegree(2)));
  tool.setSize(950,700);tool.setVisible(true);tab.splitPanes[0].setDividerLocation(0.7);
  System.out.println("BROWSER FIT READY");
 }
 public static Dataset data(int n){Dataset d=new Dataset();d.setXYColumnNames("t","y");for(int i=0;i<n;i++){double t=i/30.0;d.append(t,-1980*t*t+1067*t-3.9+0.4*Math.sin(i));}return d;}
 public static void select(int n){tab.setSelectedData(data(n),true);}
 public static void resize(int width,int height){tool.setSize(width,height);tab.splitPanes[0].setDividerLocation(0.7);tool.validate();}
 public static String snapshot(){
  JScrollPane scroll=(JScrollPane)fitter.splitPane.getRightComponent();JTable table=(JTable)scroll.getViewport().getView();
  String s=tab.splitPanes[1].getDividerLocation()+"|"+fitter.splitPane.getOrientation()+"|"+table.getRowCount();
  for(int row=0;row<table.getRowCount();row++)s+="|"+table.getValueAt(row,2);
  return s;
 }
 public static String report(){double[] sigma=new double[fitter.fit.getParameterCount()];for(int i=0;i<sigma.length;i++)sigma[i]=fitter.getUncertainty(i);return CurveFitReport.create(fitter.fit,data(16),null,sigma,true,true);}
}
