_gami_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _GAMI_COMPLETE=complete $1 ) )
    return 0
}

complete -F _gami_completion -o default gami;
