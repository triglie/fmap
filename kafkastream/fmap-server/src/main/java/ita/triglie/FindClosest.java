package ita.triglie;

public class FindClosest {

    // Returns element closest to target in arr[]
    public static float findClosest(Float[] floats, Float float1) {
        int n = floats.length;

        // Corner cases
        if (float1 <= floats[0]) return floats[0];
        if (float1 >= floats[n - 1]) return floats[n - 1];

        // Doing binary search
        int i = 0, j = n, mid = 0;
        while (i < j) {
            mid = (i + j) / 2;

            if (floats[mid] == float1)
                return floats[mid];

            /* If target is less than array element, then search in left */
            if (float1 < floats[mid]) {

                // If target is greater than previous
                // to mid, return closest of two
                if (mid > 0 && float1 > floats[mid - 1])
                    return getClosest(floats[mid - 1], floats[mid], float1);
                /* Repeat for left half */
                j = mid;
            }
            // If target is greater than mid
            else {
                if (mid < n-1 && float1 < floats[mid + 1])
                    return getClosest(floats[mid], floats[mid + 1], float1);
                i = mid + 1; // update i
            }
        }
        // Only single element left after search
        return floats[mid];
    }

    // Method to compare which one is the more close
    // We find the closest by taking the difference
    // between the target and both values. It assumes
    // that val2 is greater than val1 and target lies
    // between these two.
    private static float getClosest(float val1, float val2, float target) {
        if (target - val1 >= val2 - target)
            return val2;
        else
            return val1;
    }
}