import java.nio.file.*;
import java.util.*;
import org.eclipse.jdt.core.*;
import org.eclipse.jdt.core.dom.*;
import j2s.swingjs.Java2ScriptVisitor;
public class Transpile {
 public static void main(String[] args) throws Exception {
  String root=Path.of(args[0]).toAbsolutePath().toString();
  String out=args[1];
  Java2ScriptVisitor.NameMapper.setNonQualifiedNamePackages(null);
  Java2ScriptVisitor.NameMapper.setClassReplacements(null);
  Java2ScriptVisitor.startCleanBuild();
  Java2ScriptVisitor.setAnnotating("true");
  List<Path> files = new ArrayList<>();
  if(args[2].equals("ALL")) {
   try(var stream=Files.walk(Path.of(root,"org/opensourcephysics"))){stream.filter(p -> p.toString().endsWith(".java")).forEach(files::add);}
  } else for(int a=2;a<args.length;a++) files.add(Path.of(args[a]));
  for(Path file:files) {
   ASTParser parser=ASTParser.newParser(AST.JLS11);
   Map<String,String> options=JavaCore.getOptions();
   JavaCore.setComplianceOptions(JavaCore.VERSION_11,options);parser.setCompilerOptions(options);
   parser.setEnvironment(new String[]{Path.of(System.getProperty("test.classpath", "platform-results/classes")).toAbsolutePath().toString()},new String[]{root,Path.of(root).getParent().resolve("test").toString()},new String[]{"UTF-8","UTF-8"},true);
   parser.setUnitName(file.getFileName().toString());parser.setSource(Files.readString(file).toCharArray());parser.setResolveBindings(true);
   CompilationUnit unit=(CompilationUnit)parser.createAST(null);
   for(var problem:unit.getProblems())if(problem.isError())throw new RuntimeException(file+": "+problem);
   Java2ScriptVisitor visitor=new Java2ScriptVisitor().setProject(null,false);
   unit.accept(visitor);
   List<String> elements=visitor.getElementList();
   Path dir=Path.of(out,visitor.getMyPackageName().replace('.','/'));Files.createDirectories(dir);
   for(int i=0;i<elements.size();i+=2){Path target=dir.resolve(elements.get(i)+".js");Files.writeString(target,elements.get(i+1));System.out.println(target);}
  }
 }
}
