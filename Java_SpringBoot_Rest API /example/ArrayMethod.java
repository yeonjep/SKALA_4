public class ArrayMethod {

    public static void main(String[] args) {
        String[] users  = {"alice", "bob", "charlie"};
        int[]    scores = {85, 92, 78};

        for (int i = 0; i < users.length; i++) {
            printGrade(users[i], scores[i]);
        }
    }

    // 메서드 정의
    public static void printGrade(String name, int score) {
        System.out.println(name + " : " + score + "점");
    }

    // 오버로딩 예시 (제목과 맞추려면 이런 버전 추가)
    public static void printGrade(String name, double score) {
        System.out.println(name + " : " + score + "점 (소수 점수)");
    }
}