class MiscMixin:
    ###############################################################################################
    # Helper funcs (e.g. enum handling)
    ###############################################################################################

    @staticmethod
    def enum2tuple(my_enum):
        """
        Useful helper function to convert an Enum to a list of its values.
        Used in `check_df` and `init_df` functions.
        """
        return tuple(i.value for i in my_enum)
