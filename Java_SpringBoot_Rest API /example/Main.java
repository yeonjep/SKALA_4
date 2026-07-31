/*
Main.java
 ├─ class Animal
 ├─ class Dog extends Animal
 ├─ class Cat extends Animal
 └─ public class Main
 */

// 부모 클래스
class Animal {
    public void speak() {
        System.out.println("동물이 소리를 냅니다.");
    }
}

// 자식 클래스
class Dog extends Animal {
    @Override
    public void speak() {
        System.out.println("개가 짖습니다.");
    }
}

class Cat extends Animal {
    @Override
    public void speak() {
        System.out.println("고양이가 웁니다.");
    }
}

/*
public 클래스가 있는 경우 :
- 하나의 .java 파일에는 public 클래스는 단 하나만 가능
- 그리고 파일명은 그 public 클래스명과 반드시 같아야 함
*/
public class Main {
    public static void main(String[] args) {
        Animal a1 = new Dog(); // 다형성
        Animal a2 = new Cat();

        a1.speak(); // 개가 짖습니다.
        a2.speak(); // 고양이가 웁니다.
    }
}
