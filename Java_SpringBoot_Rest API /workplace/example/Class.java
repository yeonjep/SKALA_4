import java.util.*;

public class Class {
    public static void main(String[] args) {

        String s = "hello";
        int len = s.length();

        List<String> list = new ArrayList<>();
        list.add("A");

        Map<String, String> map = new HashMap<>();
        map.put("id", "admin");

        System.out.println(len);
        System.out.println(list);
        System.out.println(map);
    }
}